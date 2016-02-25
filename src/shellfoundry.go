package main

import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"fmt"
	"github.com/codegangsta/cli"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func overwrite(mpath string) (*os.File, error) {
	f, err := os.OpenFile(mpath, os.O_RDWR|os.O_TRUNC, 0777)
	if err != nil {
		f, err = os.Create(mpath)
		if err != nil {
			return f, err
		}
	}
	return f, nil
}

func read(mpath string) (*os.File, error) {
	f, err := os.OpenFile(mpath, os.O_RDONLY, 0444)
	if err != nil {
		return f, err
	}
	return f, nil
}

func untarIt(mpath string, basepath string) {
	fr, err := read(mpath)
	fmt.Printf("reading %s\n", mpath)

	defer fr.Close()
	if err != nil {
		panic(err)
	}
	gr, err := gzip.NewReader(fr)
	defer gr.Close()
	if err != nil {
		panic(err)
	}
	tr := tar.NewReader(gr)
	var index = 0
	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			// end of tar archive
			break
		}
		if err != nil {
			panic(err)
		}
		path := filepath.Join(basepath, hdr.Name)
		switch hdr.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(path, os.FileMode(hdr.Mode)); err != nil {
				panic(err)
			}
			fmt.Printf("creating dir %s \n", path)

		case tar.TypeReg:
			ow, err := overwrite(path)
			defer ow.Close()
			if err != nil {
				panic(err)
			}
			if _, err := io.Copy(ow, tr); err != nil {
				panic(err)
			}
			fmt.Printf("writing %s \n", path)
		default:
			fmt.Printf("Can't: %c, %s\n", hdr.Typeflag, path)
		}
		index++
	}
}

func zipIt(source, target string) error {
	zipfile, err := os.Create(target)
	if err != nil {
		return err
	}
	defer zipfile.Close()

	archive := zip.NewWriter(zipfile)
	defer archive.Close()

	filepath.Walk(source, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		/*
			FileInfoHeader creates a partially-populated FileHeader from an os.FileInfo.
			Because os.FileInfo's Name method returns only the base name of the file it describes,
			it may be necessary to modify the Name field of the returned header to provide the full path name of the file.
		*/
		header, err := zip.FileInfoHeader(info)
		if err != nil {
			return err
		}

		if info.IsDir() && path == source {
			return nil
		}

		filename := strings.TrimPrefix(path, source) // trims parent part of the path, for example: strings.TrimPrefix("template/file.txt", "template/") -> "file.txt"
		if filename != "" {
			header.Name = filename
		}

		if info.IsDir() {
			header.Name += "/"
		} else {
			header.Method = zip.Deflate
		}

		/**
		CreateHeader adds a file to the zip file using the provided FileHeader for the file metadata.
		It returns a Writer to which the file contents should be written.

		The file's contents must be written to the io.Writer before the next call to Create, CreateHeader, or Close.
		The provided FileHeader fh must not be modified after a call to CreateHeader.
		*/
		writer, err := archive.CreateHeader(header)
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}
		fmt.Println(path)
		file, err := os.Open(path)
		if err != nil {
			return err
		}
		defer file.Close()

		/**
		Copy copies from src to dst until either EOF is reached on src or an error occurs.
		It returns the number of bytes copied and the first error encountered while copying, if any.

		A successful Copy returns err == nil, not err == EOF. Because Copy is defined to read from src until EOF,
		it does not treat an EOF from Read as an error to be reported.

		If src implements the WriterTo interface, the copy is implemented by calling src.WriteTo(dst).
		Otherwise, if dst implements the ReaderFrom interface, the copy is implemented by calling dst.ReadFrom(src).
		*/

		_, err = io.Copy(writer /*dst*/, file /*src*/)
		return err
	})

	return err
}

func downloadFromUrl(url string) (filename string, err error) {

	temp_file, err := ioutil.TempFile(os.TempDir(), "shelltemp_")

	fmt.Println("Downloading", url, "to", temp_file.Name())
	defer temp_file.Close()

	response, err := http.Get(url)
	if err != nil {
		return "", fmt.Errorf("Error while downloading", url, "-", err)
	}
	defer response.Body.Close()

	n, err := io.Copy(temp_file, response.Body)
	if err != nil || n == 0 {
		return "", fmt.Errorf("Error while downloading", url, "-", err)
	}

	return temp_file.Name(), nil
}

func Unzip(src, dest string) error {
	r, err := zip.OpenReader(src)
	if err != nil {
		return err
	}
	defer func() {
		if err := r.Close(); err != nil {
			panic(err)
		}
	}()

	os.MkdirAll(dest, 0755)

	// Closure to address file descriptors issue with all the deferred .Close() methods
	extractAndWriteFile := func(f *zip.File, root_dir string) error {
		rc, err := f.Open()
		if err != nil {
			return err
		}
		defer func() {
			if err := rc.Close(); err != nil {
				panic(err)
			}
		}()

		relative_path := strings.Replace(f.Name, root_dir, "", 1)
		path := filepath.Join(dest, relative_path)

		if f.FileInfo().IsDir() {
			os.MkdirAll(path, f.Mode())
		} else {
			f, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, f.Mode())
			if err != nil {
				return err
			}
			defer func() {
				if err := f.Close(); err != nil {
					panic(err)
				}
			}()

			_, err = io.Copy(f, rc)
			if err != nil {
				return err
			}
		}
		return nil
	}

	first := true
	root_dir := ""
	for _, f := range r.File {
		if first {
			root_dir = f.Name
		} else {
			err := extractAndWriteFile(f, root_dir)
			if err != nil {
				return err
			}

		}

		first = false

	}

	return nil
}

func main() {
	app := cli.NewApp()
	app.Version = "0.0.1"
	app.Name = "shellfoundry"
	app.Usage = "CloudShell package CLI build tool. Use 'shellfoundry help' for more options"

	app.Commands = []cli.Command{
		{
			Name:    "create",
			Aliases: []string{"c"},
			Usage:   "create directory structure for the package template, takes as input the name of the shell.",
			Action: func(c *cli.Context) {
				directory := c.Args()[0]
				url := "https://api.github.com/repos/doppleware/shell_templates/zipball"
				filename, err := downloadFromUrl(url)
				if err != nil {
					fmt.Println("Error while creating dir")
					return
				}
				os.Mkdir(directory, 0777)
				Unzip(filename, directory)
				os.Remove(filename)
			},
		},
		{
			Name:    "download",
			Aliases: []string{"d"},
			Usage:   "download shell template from github",
			Action: func(c *cli.Context) {
				url := "https://api.github.com/repos/doppleware/shell_templates/tarball"
				downloadFromUrl(url)
				str, err := ioutil.TempDir("", "shelltemp_")
				fmt.Println(str)
				if err != nil {
					fmt.Println("Error while creating dir")
					return
				}
				untarIt("test.zip", str)
			},
		},
		{
			Name:    "pack",
			Aliases: []string{"p"},
			Usage:   "create package.zip",
			Action: func(c *cli.Context) {
				zipIt("template", "package.zip")
			},
		},
		{
			Name:    "publish",
			Aliases: []string{"u"},
			Usage:   "publish package to CloudShell",
			Action: func(c *cli.Context) {
			},
		},
	}
	app.Run(os.Args)
}
