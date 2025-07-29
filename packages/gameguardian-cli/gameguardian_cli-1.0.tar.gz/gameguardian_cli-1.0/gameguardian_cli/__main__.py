from .cli import GameGuardianShell

def main():
    shell = GameGuardianShell()
    shell.cmdloop()

if __name__ == '__main__':
    main()