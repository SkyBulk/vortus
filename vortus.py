import sys
import optparse

def main():
    parser = optparse.OptionParser()
    parser.add_option("-q", "--quiet", dest="quiet_mode_opt", action="store_true", default=False, help="Runs without displaying the banner.")
    parser.add_option("-p", "--profile", dest="profile", help="Load vortus profile.")
    options,r = parser.parse_args()

    if options.profile:
        from core.shell import Shell
        pass
    else:
        from core.shell import Shell
        shell = Shell()
        shell.shell()


if __name__ == '__main__':
    main()
