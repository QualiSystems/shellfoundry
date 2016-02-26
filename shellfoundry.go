package main

import (
	"archive/tar"
	"archive/zip"
	"compress/gzip"
	"encoding/xml"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/codegangsta/cli"
)

type Driver struct {
	Name string `xml:"Name,attr"`
}

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

func untarIt(mpath string, basepath string, root string) {
	fr, err := read(mpath)
	//fmt.Printf("reading %s\n", mpath)

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
	var topDir = ""
	var firstDir = true

	for {
		hdr, err := tr.Next()
		if err == io.EOF {
			// end of tar archive
			break
		}
		if err != nil {
			panic(err)
		}
		originalPath := hdr.Name
		//fmt.Printf("current fie %s \n", originalPath)
		path := filepath.Join(basepath, strings.Replace(hdr.Name, topDir, "", -1))
		switch hdr.Typeflag {
		case tar.TypeDir:
			if firstDir == true {
				if filepath.Base(originalPath) == root {
					topDir = originalPath
					firstDir = false
					//fmt.Printf("Setting the top folder %s \n", topDir)
				}
			} else if strings.HasPrefix(originalPath, topDir) {

				if err := os.MkdirAll(path, os.FileMode(hdr.Mode)); err != nil {
					panic(err)
				}
				//fmt.Printf("creating dir %s \n", path)
			}

		case tar.TypeReg:
			if firstDir == false && strings.HasPrefix(originalPath, topDir) {
				ow, err := overwrite(path)
				defer ow.Close()
				if err != nil {
					panic(err)
				}
				if _, err := io.Copy(ow, tr); err != nil {
					panic(err)
				}
				//fmt.Printf("writing %s \n", path)
			}

		default:
			//fmt.Printf("Can't: %c, %s\n", hdr.Typeflag, path)
		}
		index++
	}
}

func zipIt(source, target string, excludedExtensions []string) error {
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

		filename := strings.TrimPrefix(path, source)
		filename = strings.TrimPrefix(filename, "/") // trims parent part of the path, for example: strings.TrimPrefix("template/file.txt", "template/") -> "file.txt"
		for index := 0; index < len(excludedExtensions); index++ {
			if strings.HasSuffix(strings.ToLower(filename), strings.ToLower(excludedExtensions[index])) {
				return nil
			}

		}
		if filename != "" {
			header.Name = filename
		}

		if info.IsDir() {
			//fmt.Println("dir: " + info.Name())
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
		//fmt.Println("header: " + header.Name)
		writer, err := archive.CreateHeader(header)
		if err != nil {
			return err
		}

		if info.IsDir() {
			return nil
		}
		//fmt.Println(path)
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

func downloadFromURL(url string) (filename string, err error) {

	temp_file, err := ioutil.TempFile(os.TempDir(), "shelltemp_")

	//fmt.Println("Downloading", url, "to", temp_file.Name())
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

// Copies file source to destination dest.
func CopyFile(source string, dest string) (err error) {
	sf, err := os.Open(source)
	if err != nil {
		return err
	}
	defer sf.Close()
	df, err := os.Create(dest)
	if err != nil {
		return err
	}
	defer df.Close()
	_, err = io.Copy(df, sf)
	if err == nil {
		si, err := os.Stat(source)
		if err != nil {
			err = os.Chmod(dest, si.Mode())
		}

	}

	return
}

func CreateDirIfNotExists(path string) (err error) {
	// create dest dir if needed
	_, err = os.Open(path)
	if os.IsNotExist(err) {
		err = os.MkdirAll(path, 0777)
		if err != nil {
			return err
		}
	}
	return nil
}

// Recursively copies a directory tree, attempting to preserve permissions.
// Source directory must exist, destination directory must *not* exist.
func CopyDir(source string, dest string) (err error) {

	// get properties of source dir
	fi, err := os.Stat(source)
	if err != nil {
		return err
	}

	if !fi.IsDir() {
		return &CustomError{"Source is not a directory"}
	}

	// create dest dir if needed
	err = CreateDirIfNotExists(dest)
	if err != nil {
		return err
	}

	// ensure dest dir does not already exist

	entries, err := ioutil.ReadDir(source)

	for _, entry := range entries {

		sfp := source + "/" + entry.Name()
		dfp := dest + "/" + entry.Name()
		if entry.IsDir() {
			err = CopyDir(sfp, dfp)
			if err != nil {
				log.Println(err)
			}
		} else {
			// perform copy
			err = CopyFile(sfp, dfp)
			if err != nil {
				log.Println(err)
			}
		}

	}
	return
}

// A struct for returning custom error messages
type CustomError struct {
	What string
}

// Returns the error message defined in What as a string
func (e *CustomError) Error() string {
	return e.What
}

func Copy(dst, src string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	out, err := os.Create(dst)

	if err != nil {
		return err
	}

	defer out.Close()
	_, err = io.Copy(out, in)
	cerr := out.Close()
	if err != nil {
		return err
	}
	fmt.Println("Copied DST:" + dst)

	return cerr
}

func parseXML(filename string) string {
	xmlFile, err := os.Open(filename)
	if err != nil {
		fmt.Println("Error opening file:", err)
		return ""
	}
	defer xmlFile.Close()
	b, _ := ioutil.ReadAll(xmlFile)

	var q Driver

	xml.Unmarshal(b, &q)

	return q.Name

}

func replaceString(file string, match string, replace string) {
	input, err := ioutil.ReadFile(file)
	if err != nil {
		log.Fatalln(err)
	}

	lines := strings.Split(string(input), "\n")

	for i, line := range lines {
		if strings.Contains(line, match) {
			lines[i] = strings.Replace(line, match, replace, -1)
		}
	}
	output := strings.Join(lines, "\n")
	err = ioutil.WriteFile(file, []byte(output), 0644)
	if err != nil {
		log.Fatalln(err)
	}
}
func downloadTemplate(template string) (directory string, err error) {
	url := "https://api.github.com/repos/QualiSystems/shell-templates/tarball/new_format"
	zipfile, err := downloadFromURL(url)
	if err != nil {
		fmt.Println("Error while downloading", url, "-", err)
		return "", err
	}
	packageTempDir := filepath.Join(os.TempDir(), "spool_"+filepath.Base(zipfile))
	os.MkdirAll(packageTempDir, 0777)
	untarIt(zipfile, packageTempDir, template)
	return packageTempDir, nil
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
			Usage:   "create directory structure for the package template. \n e.g shellfoundry create myshell ",
			Action: func(c *cli.Context) {

				template := "base"
				packageTempDir, err := downloadTemplate(template)
				if err != nil {
					fmt.Println("Error while downloading template: " + err.Error())
					return
				}

				if len(c.Args()) < 0 {
					fmt.Println("Usage: shellfoundry create [shellname]  ")
					return
				}
				directory := c.Args()[0]

				dataModelDir := filepath.Join(directory, "datamodel")
				distDir := filepath.Join(directory, "dist")
				srcDir := filepath.Join(directory, "src")
				scriptsDir := filepath.Join(directory, "scripts")

				err = CreateDirIfNotExists(dataModelDir)
				if err != nil {
					fmt.Println("Error while copying template: " + err.Error())
				}
				err = CopyDir(packageTempDir, directory)
				if err != nil {
					fmt.Println("Error while copying template: " + err.Error())
				}

				templateName := template + "Shell"

				err = CreateDirIfNotExists(scriptsDir)
				if err != nil {
					fmt.Println("Error while copying template: " + err.Error())
				}
				err = CreateDirIfNotExists(distDir)
				if err != nil {
					fmt.Println("Error while copying template: " + err.Error())
				}

				os.Rename(filepath.Join(srcDir, strings.ToLower(templateName)+"driver.py"),
					filepath.Join(srcDir, directory+"driver.py"))

				replaceString(filepath.Join(srcDir, "drivermetadata.xml"),
					fmt.Sprintf("<Driver Name=\"%s Driver\"", strings.Title(templateName)),
					fmt.Sprintf("<Driver Name=\"%s\"", strings.Title(directory+" driver")))

				replaceString(filepath.Join(srcDir, "drivermetadata.xml"),
					fmt.Sprintf("MainClass=\"%sdriver.%sDriver\"", strings.ToLower(templateName),
						strings.Title(templateName)),
					fmt.Sprintf("MainClass=\"%s\"", directory+"driver."+strings.Title(directory+"Driver")))

				replaceString(filepath.Join(srcDir, directory+"driver.py"),
					fmt.Sprintf("class %sDriver", strings.Title(templateName)),
					fmt.Sprintf("class %s", strings.Title(directory+"Driver")))

				replaceString(filepath.Join(dataModelDir, "datamodel.xml"),
					fmt.Sprintf("<ResourceModel Name=\"%s\"", strings.Title(templateName)),
					fmt.Sprintf("<ResourceModel Name=\"%s\"", strings.Title(directory)))

				replaceString(filepath.Join(dataModelDir, "datamodel.xml"),
					fmt.Sprintf("<DriverDescriptor Name=\"%s\"", strings.Title(templateName+" driver")),
					fmt.Sprintf("<DriverDescriptor Name=\"%s\"", strings.Title(directory+" driver")))

				replaceString(filepath.Join(dataModelDir, "datamodel.xml"),
					fmt.Sprintf("<DriverName>%s</DriverName>", strings.Title(templateName+" Driver")),
					fmt.Sprintf("<DriverName>%s</DriverName>", strings.Title(directory+" Driver")))

				replaceString(filepath.Join(dataModelDir, "shellconfig.xml"),
					fmt.Sprintf("<ResourceTemplate Name=\"%s\" Model=\"%s\" Driver=\"%s\">",
						strings.Title(templateName), strings.Title(templateName), strings.Title(templateName+" driver")),
					fmt.Sprintf("<ResourceTemplate Name=\"%s\" Model=\"%s\" Driver=\"%s\">",
						strings.Title(directory), strings.Title(directory), strings.Title(directory+" driver")))

				err = os.RemoveAll(packageTempDir)
				if err != nil {
					fmt.Println("Error deleting temp files: " + err.Error())
					return
				}

			},
		},

		{
			Name:    "package",
			Aliases: []string{"p"},
			Usage:   "shellfoundry package",
			Action: func(c *cli.Context) {

				driverName := parseXML(filepath.Join("src", "drivermetadata.xml"))
				driverPath := filepath.Join(os.TempDir(), driverName) + ".zip"
				excludedExt := []string{".ds_store", ".gitignore"}
				errr := zipIt("src", driverPath, excludedExt)
				if errr != nil {
					fmt.Println("Error while packaging driver: " + errr.Error())
					return
				}
				template := "package_template"

				packageTempDir, err := downloadTemplate(template)
				if err != nil {
					fmt.Println("Error while downloading template: " + err.Error())
					return
				}
				err = Copy(filepath.Join(packageTempDir, "Resource Drivers - Python", filepath.Base(driverPath)),
					driverPath)

				if err != nil {
					fmt.Println("Error while copying driver " + err.Error())
					return
				}

				err = Copy(filepath.Join(packageTempDir, "DataModel", "datamodel.xml"), filepath.Join("DataModel", "datamodel.xml"))
				if err != nil {
					fmt.Println("Error while copying data model: " + err.Error())
					return
				}
				err = Copy(filepath.Join(packageTempDir, "Configuration", "shellconfig.xml"), filepath.Join("DataModel", "shellconfig.xml"))
				if err != nil {
					fmt.Println("Error while copying configuration: " + err.Error())
					return
				}

				currentDir, err := os.Getwd()
				if err != nil {
					fmt.Println("Error while getting current dir: " + err.Error())
					return
				}
				//fmt.Println(packageTempDir)

				zipIt(packageTempDir, filepath.Join("dist", filepath.Base(currentDir)+".zip"), excludedExt)
				if err != nil {
					fmt.Println("Error creating package: " + err.Error())
					return
				}
				err = os.RemoveAll(packageTempDir)
				if err != nil {
					fmt.Println("Error deleting temp files: " + err.Error())
					return
				}
				// excludedExt := []string{".ds_store"}
				// temp_file, err := ioutil.TempFile(os.TempDir(), "shelltemp_")
				// if err != nil {
				// 	fmt.Println("Error while creating dir")
				// 	return
				// }
				// zipIt("src", temp_file.Name(), excludedExt)
				//
				// zipIt("template", "package.zip", excludedExt)
			},
		},
		{
			Name:    "publish",
			Aliases: []string{"u"},
			Usage:   "Not yet implemented",
			Action: func(c *cli.Context) {
			},
		},
	}
	app.Run(os.Args)
}
