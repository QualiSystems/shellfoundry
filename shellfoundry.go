package main

import (
	"archive/tar"
	"compress/gzip"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"os"
	"path/filepath"
	"archive/zip"
	"strings"
	"github.com/codegangsta/cli"
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

		header, err := zip.FileInfoHeader(info)
		if err != nil {
			return err
		}

		filename := strings.TrimPrefix(path, source)
		if filename != "" {
			header.Name = filepath.Join(filename)
		}

		if info.IsDir() {
			header.Name += "/"
		} else {
			header.Method = zip.Deflate
		}

		writer, err := archive.CreateHeader(header)
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}
		file, err := os.Open(path)
		if err != nil {
			return err
		}
		defer file.Close()
		_, err = io.Copy(writer, file)
		return err
	})

	return err
}

func downloadFromUrl(url string) {
	fileName := "test.zip"
	fmt.Println("Downloading", url, "to", fileName)

	// TODO: check file existence first with io.IsExist
	output, err := os.Create(fileName)
	if err != nil {
		fmt.Println("Error while creating", fileName, "-", err)
		return
	}
	defer output.Close()

	response, err := http.Get(url)
	if err != nil {
		fmt.Println("Error while downloading", url, "-", err)
		return
	}
	defer response.Body.Close()

	n, err := io.Copy(output, response.Body)
	if err != nil {
		fmt.Println("Error while downloading", url, "-", err)
		return
	}

	fmt.Println(n, "bytes downloaded.")
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
			Usage:   "create directory structure for the package template",
			Action: func(c *cli.Context) {
				os.MkdirAll("template" + string(filepath.Separator) + "DataModel", 0777)
				os.MkdirAll("template" + string(filepath.Separator) + "Resource Scripts", 0777)
				os.Create("template" + string(filepath.Separator) + "DataModel" + string(filepath.Separator) + "datamodel.xml")
				os.Create("template" + string(filepath.Separator) + "Resource Scripts" + string(filepath.Separator) + "metadata.xml")
			},
		},
		{
			Name: 	 "download",
			Aliases: []string{"d"},
			Usage: 	 "download shell template from github",
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
			Name: 	 "pack",
			Aliases: []string{"p"},
			Usage:	 "create package.zip",
			Action: func(c *cli.Context) {
				zipIt("template", "package.zip")
			},
		},
		{
			Name: 	 "publish",
			Aliases: []string{"u"},
			Usage:	 "publish package to CloudShell",
			Action: func(c *cli.Context) {
			},
		},
	}
	app.Run(os.Args)
}
