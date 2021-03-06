'''
@author: shwang
'''
import os

serverBuild = {"staging":     "-staging-ui-api14-release-armv7.apk",
               "staging2":     "-staging2-ui-api14-release-armv7.apk",
               "production":  "-production-ui-api14-release-armv7.apk",
               "t2dev":       "-t2dev-ui-api14-release-armv7.apk",
               "addev":       "-addev-ui-api14-release-armv7.apk",
               "chaosdev":    "-chaosdev-ui-api14-release-armv7.apk",
               "cidev":       "-ci-ui-api14-release-armv7.apk",
               "dragondev":   "-dragondev-ui-api14-release-armv7.apk",
               "fludev":      "-fludev-ui-api14-release-armv7.apk",
               "gemdev":      "-gemdev-ui-api14-release-armv7.apk",
               "maddev":      "-maddev-ui-api14-release-armv7.apk",
               "newmandev":   "-newmandev-ui-api14-release-armv7.apk",
               "videodev":    "-videodev-ui-api14-release-armv7.apk",
               "xdev":        "-xdev-ui-api14-release-armv7.apk",
               "int1":        "-int1-ui-api14-release-armv7.apk",
               "int2":        "-int1-ui-api14-release-armv7.apk",
               "int3":        "-int1-ui-api14-release-armv7.apk",
               "t2dev_ios":   "-tango_t2dev_inhouse_tango3dev_release-fat.ipa",
               "staging_ios": "-tango_staging_inhouse_tango3dev_release-fat.ipa",
               "prod_ios":    "-tango_production_inhouse_tango3dev_release-fat.ipa",
               "int1_ios":    "-tango_int1_inhouse_tango3dev_release-fat.ipa",
               "int2_ios":    "-tango_int2_inhouse_tango3dev_release-fat.ipa",
               "int3_ios":    "-tango_int3_inhouse_tango3dev_release-fat.ipa"
               }

newServerBuild = {"tango_staging":     "-staging-tango-release-armv7.apk",
               "tango_staging2":     "-staging2-tango-release-armv7.apk",
               "tango_production":  "-production-tango-release-armv7.apk",
               "tango_t2dev":       "-t2dev-tango-release-armv7.apk",
               "tango_addev":       "-addev-tango-release-armv7.apk",
               "tango_chaosdev":    "-chaosdev-tango-release-armv7.apk",
               "tango_cidev":       "-ci-tango-release-armv7.apk",
               "tango_dragondev":   "-dragondev-tango-release-armv7.apk",
               "tango_fludev":      "-fludev-tango-release-armv7.apk",
               "tango_gemdev":      "-gemdev-tango-release-armv7.apk",
               "tango_maddev":      "-maddev-tango-release-armv7.apk",
               "tango_newmandev":   "-newmandev-tango-release-armv7.apk",
               "tango_videodev":    "-videodev-tango-release-armv7.apk",
               "tango_xdev":        "-xdev-tango-release-armv7.apk",
               "tango_int1":        "-int1-tango-release-armv7.apk",
               "tango_int2":        "-int1-tango-release-armv7.apk",
               "tango_int3":        "-int1-tango-release-armv7.apk",
               "mango_staging":     "-staging-mango-release-armv7.apk",
               "mango_staging2":     "-staging2-mango-release-armv7.apk",
               "mango_production":  "-production-mango-release-armv7.apk",
               "mango_t2dev":       "-t2dev-mango-release-armv7.apk",
               "mango_addev":       "-addev-mango-release-armv7.apk",
               "mango_chaosdev":    "-chaosdev-mango-release-armv7.apk",
               "mango_cidev":       "-ci-mango-release-armv7.apk",
               "mango_dragondev":   "-dragondev-mango-release-armv7.apk",
               "mango_fludev":      "-fludev-mango-release-armv7.apk",
               "mango_gemdev":      "-gemdev-mango-release-armv7.apk",
               "mango_maddev":      "-maddev-mango-release-armv7.apk",
               "mango_newmandev":   "-newmandev-mango-release-armv7.apk",
               "mango_videodev":    "-videodev-mango-release-armv7.apk",
               "mango_xdev":        "-xdev-mango-release-armv7.apk",
               "mango_int1":        "-int1-mango-release-armv7.apk",
               "mango_int2":        "-int1-mango-release-armv7.apk",
               "mango_int3":        "-int1-mango-release-armv7.apk",
               "t2dev_ios":   "-tango_t2dev_inhouse_tango3dev_release-fat.ipa",
               "staging_ios": "-tango_staging_inhouse_tango3dev_release-fat.ipa",
               "prod_ios":    "-tango_production_inhouse_tango3dev_release-fat.ipa",
               "int1_ios":    "-tango_int1_inhouse_tango3dev_release-fat.ipa",
               "int2_ios":    "-tango_int2_inhouse_tango3dev_release-fat.ipa",
               "int3_ios":    "-tango_int3_inhouse_tango3dev_release-fat.ipa"
               }


releaseName = {"K":      "kabinett",
               "L":      "lambrusco",
               "Tr":     "trunk",
               "Nearby": "nearbuy-trunk",
               "M":       "muscadelle",
               "N":       "nebbiolo",
               "trunk": "trunk"
               }

localPath = {"local_win": "C:\\Users\\shwang\\Downloads\\",
             "local_mac": "~/Download/",
             "local_linux": "~/Download/",
             "current_dir": os.getcwd() + os.path.sep,
             "desktop_win_shwang":"C:\\Users\\shwang\\Desktop\\"}

urlForDownloading = {"shareCN_win": os.path.normcase("\\\sharecn.tango.corp\\share\\TangoBuilds\\"),
                     "shareCN_mac": "/Volumes/share/TangoBuilds/",
                     "shareCN_linux": "/Volumes/share/TangoBuilds/",
                     "artifactory_tango": "http://artifactory.tango.corp/tango-release/",
                     "artifactory_mango": "http://artifactory.tango.corp/mango-current/"}