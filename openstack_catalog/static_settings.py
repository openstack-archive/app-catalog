import xstatic.main
import xstatic.pkg.angular
import xstatic.pkg.magic_search

def get_staticfiles_dirs(webroot='/'):
    return [
        ('lib/angular',
            xstatic.main.XStatic(xstatic.pkg.angular,
                                 root_url=webroot).base_dir),
        ('lib/magic_search',
            xstatic.main.XStatic(xstatic.pkg.magic_search,
                                 root_url=webroot).base_dir),
    ]
