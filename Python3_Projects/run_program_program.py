import os


def basic_path():
    program = input('Run file: ')
    program_path = None
    for path, folder, files in os.walk('C:/'):
        if program in files:
            program_path = os.path.join(path, program)

    if program_path:
        run_file = os.startfile(program_path)
        print('Running:', program_path.replace('\\', '/'))
        print(run_file)
    else:
        print('\nFile Not Found')
        basic_path()


basic_path()

