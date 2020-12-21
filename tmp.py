class FileHandler:
    def write_to_file(self, file_name, content):
        with open(file_name, 'w', encoding='utf-8') as output_file:
            output_file.write(content)


def clear_characters(input_file_name, output_file_name):
    correct_characters = '1234567890ячсмитьбюфывапролджэйцукенгшщзхъёzxcvbnmasdfghjklqwertyuiop!.,:; \n'.lower()
    result = ''

    with open(input_file_name, encoding='utf-8') as file:
        for line in file:
            for character in line:
                if character.lower() in correct_characters:
                    result += character
                else:
                    result += ' '

    FileHandler().write_to_file(output_file_name, result)


def get_characters(input_file_name, output_file_name):
    characters = set()

    with open(input_file_name, encoding='utf-8') as file:
        for line in file:
            for character in line:
                characters.add(character.lower())

    FileHandler().write_to_file(output_file_name, str(characters))


def main():
    clear_characters('vova/vova.txt', 'vova/clear_vova.txt')
    get_characters('vova/vova.txt', 'vova/analiz_vova.txt')
    get_characters('vova/clear_vova.txt', 'vova/analiz_clear_vova.txt')

    print("end")


if __name__ == '__main__':
    main()