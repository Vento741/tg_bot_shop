# Приветственное сообщение
register_message = ('Приветствуею Вас,что бы совершить покупку в моём магазине \n\n'
                    'Зарегистрируйтесь 👇')

start_message = ('Приветствуею Вас!\n\n'
                 '*******************************\n\n'
                 'C помощью бота "TG_MAGNAT" вы сможете приобрести TG_аккаунты в формате Session+Json ')


# Главное меню
register_kb_text = "🔑 Зарегистрироваться "
start_catalog_text = "🔥 Каталог товаров 🔥"
start_order_text = "👀 Заказы"
start_basket_text = "🛒 Корзина"


cmd_cancel_text = "❌ Действие отменено"


# текст для handlers "Product"
category_create_product = ("Отлично, ты выбрал категорию: %s \n\n"
                           "Теперь вводи название товара: ")

img_createproduct = "Я запомнил имя, укажи картинку: "

image_susses = ("👍 Картинка добавлена  \n\n"
                "🔥 Теперь введи описание: ")

createproduct_price = ("✅ Цена сохранена \n\n"
                       "❕ Укажи ссылку на товар: ")

create_finish_text = "✅ Товар успешно добавлен в базу данных"

error_create_finish_text = "❌ Ошибка при добавлении в базу данных"

kb_buy_oneclick = "☝️ Купить в 1 клик"
kb_add_basket = "🛒 Добавить в корзину"
kb_delete_basket = "❌ Удалить из корзины"


dictionary_card_product = f'Описание: \n\n %s \n\n 🔥 Цена: %s руб.'
category_not_found = '😞 В категории пока отсутствуют товары'

# Текст для handlers "Basket"

kb_go_decoration = '✨ Перейти к оформлению'
kb_clear_basket = '🌪 Очистить корзину'
kb_go_pay = '💰 Перейти к оплате'
basket_null = '📦 Ваша корзина пуста'
basket_ok_delete = '✅ Товар убран из корзины'
basket_ok_delete_full = '✅ Корзина очищена'

order_text = ('📝 Заказ No%s \n\n'
              'Статус заказа: %s \n\n'
              'Сумма заказа: %s руб. \n\n'
              'Состав заказа\n'
               '%s')

basket_order_check = ('Давайте сверим ваш заказ. \n\n'
                      'В корзине %s Аккаунтов: \n\n'
                      '%s \n\n'
                      'Ваша сумма заказа: %s руб.')