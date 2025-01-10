def seconds_to_mm_ss(seconds):
    minutes = seconds // 60  # Целочисленное деление для получения минут
    seconds = seconds % 60    # Остаток от деления для получения секунд
    return f"{minutes:02}:{seconds:02}"  # Форматируем в виде mm:ss

# Пример использования
total_seconds = 5999  # Например, 125 секунд
formatted_time = seconds_to_mm_ss(total_seconds)
print(formatted_time)  # Вывод: 02:05
