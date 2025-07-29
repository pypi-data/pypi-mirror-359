import main as atomfoxapi

atom = atomfoxapi.Atom('Basic ZX...') # Токен авторизации

response = atom.send_notification('title', 'message', 1234567) # отправляем уведомление

if response:
    print('Успешно!')
else:
    print('Произошла ошибка.')

# скрипт отправляет уведомление в приложение пользователю с id 1234567
# ТРЕБУЕМАЯ РОЛЬ >= General manager (та, с которой доступна вкладка Customers)