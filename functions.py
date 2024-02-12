import random

my_bot_api = '5629818025:AAE3CAZFs6uhMcWZodFUdpKhSJu5awmGK_o'
poke_bot_api = "6831587612:AAEUQ4m30-Pajetdnw0AwZ4omaNmzVkc-4o"
def pokemon_catch():  # возвращает рандомное имя покемона в зависимости от их вероятности выпадения
    dictio = {'0': ['Хуйлуша'],  # key - веротность выпаения покемона, value -  list с именами покемонов
              '10': ['Pikachu'],
              '0': ['Лох'],               # вероятности должны в сумме давать 100
              '40': ['Squirtle', 'Bulbasaur'],
              '50': ['Charmander'], }
    rand_num = random.randint(1, 100)
    counter = 0
    for key in dictio:
        counter += int(key)
        if counter >= rand_num:
            pokemon_name = random.choice(dictio[key])
            return pokemon_name

if __name__ == "__main__":
    pokemon_catch()
