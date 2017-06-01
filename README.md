# KMHXcodeTools
## Last Updated: Jun 01 2017

This Python script keeps your `project.pbxproj` file inside of your `<ProjectName>.xcodeproj` file organized.

### How To Use

Copy pbxproj_organizer.py into your Xcode project's directory so it is a sibling of your `.xcodeproj` file. Then add the following Run Script to your Build Phases to have Xcode automatically keep your `project.pbxproj` file organized each time you build your app:

![Xcode Run Script][img_runscript]

or you can navigate to your project's directory and run it via the Terminal:
```
$ python pbxproj_organizer.py
```

[img_runscript]: pbxproj_run_script.png "Xcode Run Script"
