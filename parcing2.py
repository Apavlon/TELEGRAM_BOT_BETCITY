from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # Включаем headless-режим
# Отключаем использование GPU (опционально)
options.add_argument('--disable-gpu')
# Задаём размер окна, чтобы избежать проблем с отображением
options.add_argument('--window-size=1920,1080')


def match_info():
    # Установка WebDriver с использованием ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://betcity.ru/ru/live/soccer")

    # Инициализация списка для хранения данных о матчах
    info = []

    try:
        # Ждём загрузки списка матчей
        containers = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "line-event__name-team"))
        )

        for index, container in enumerate(containers):
            try:
                # Обновляем список контейнеров только после возврата
                container = containers[index]

                # Пропускаем пустые элементы
                if not container.text.strip():
                    continue

                # Собираем данные о командах
                two_team = container.text.replace('\n', ' - ')
                print(f"Обрабатывается матч: {two_team}")

                # Проверяем, есть ли красные карточки в матче
                red_card_element = container.find_elements(
                    By.CLASS_NAME, "line-event__red-card"
                )

                if not red_card_element:
                    print(f"Матч {two_team} пропущен: нет красных карточек.")
                    continue

                statistics = re.search(
                    r"(УГЛ|ЖК|удары в створ|фолы|офсайды|ауты|удары от ворот|выход мед. бригады на поле|уд. в штангу/перекладину)", two_team)
                if statistics:
                    print(f"Статистику матчей не рассматриваем: "
                          f"{statistics.group()}")
                else:

                    # Скроллим и проверяем кликабельность
                    driver.execute_script(
                        "arguments[0].scrollIntoView(true);", container)
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "line-event__name-team")))
                    container.click()

                    # Сбор данных о матче
                    try:
                        score = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME,
                                 "scoreboard-content__main-score")
                            )
                        ).text
                        print(score)
                        parts = score.split(":")
                        score_t_1, score_t_2 = int(parts[0]), int(parts[1])

                        match_time_2 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "scoreboard-content__info")
                            )
                        ).text
                        print(match_time_2)
                        try:
                            # Попытка получить данные о красных карточках
                            red_card_1 = "0"  # Значение по умолчанию
                            red_card_2 = "0"  # Значение по умолчанию

                            try:
                                red_card_1 = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH,
                                         "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[2]/span[5]")
                                    )
                                ).text
                                print(f"TEST redcard1 {red_card_1}")
                            except Exception:
                                try:
                                    red_card_1 = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH, "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/div[1]/div[1]/div/span[1]")
                                        )
                                    ).text
                                    print(f"TEST redcard1(2) {red_card_1}")
                                except Exception:
                                    print(
                                        "Ошибка при получении red_card_1. Установлено значение по умолчанию: 0")

                            try:
                                red_card_2 = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH,
                                            "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[3]/span[5]")
                                    )
                                ).text
                                print(f"TEST redcard2(1) {red_card_2}")
                            except Exception:
                                try:
                                    red_card_2 = WebDriverWait(driver, 5).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH,
                                                "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/div[1]/div[3]/div/span[2]")
                                        )
                                    ).text
                                    print(f"TEST redcard2(2) {red_card_2}")
                                except Exception:
                                    print(
                                        "Ошибка при получении red_card_2. Установлено значение по умолчанию: 0")
                                # После обработки данных по красным карточкам вы продолжаете сбор остальной информации
                            print(f"Красные карточки: {
                                  red_card_1}, {red_card_2}")
                        except Exception as e:
                            print(
                                f"Ошибка при сборе информации о красных карточках: {e}")

                        corner_1 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[2]/span[3]")
                            )
                        ).text
                        print(corner_1)
                        corner_2 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[3]/span[3]")
                            )
                        ).text
                        print(corner_2)

                        kick_on_gate_1 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[2]/span[10]")
                            )
                        ).text
                        print(kick_on_gate_1)
                        kick_on_gate_2 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[3]/span[10]")
                            )
                        ).text
                        print(kick_on_gate_2)

                        kick_on_target_1 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[2]/span[9]")
                            )
                        ).text
                        print(kick_on_target_1)
                        kick_on_target_2 = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 "/html/body/app-root/main/div/app-live-bets/app-scoreboard/div/div/div[2]/app-scoreboard-simple/app-livestat-table-info/div/div[3]/span[9]")
                            )
                        ).text
                        print(kick_on_target_2)

                        fact_end = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME,
                                 "dops-item__title")
                            )
                        ).text
                        print(fact_end)
                        if fact_end == "ФАКТИЧЕСКИЙ ИСХОД":

                            try:
                                coeff_1 = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH,
                                         "/html/body/app-root/main/div/app-live-bets/div/div/app-ext-dops-container/div[2]/div[1]/app-dop-ext[1]/div/div[2]/div/div/div[1]/div/button")
                                    )
                                ).text
                                print(f"коэфф1 {coeff_1}")
                            except Exception as e:
                                print(
                                    f"Коэффициент первой команды не найден: {e}")

                            try:
                                coeff_2 = WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH,
                                         "/html/body/app-root/main/div/app-live-bets/div/div/app-ext-dops-container/div[2]/div[1]/app-dop-ext[1]/div/div[2]/div/div/div[3]/div/button")
                                    )
                                ).text
                                print(f"коэфф2 {coeff_2}")

                            except Exception as e:
                                print(
                                    f"Коэффициент второй команды не найден: {e}")
                        else:
                            print(f"{fact_end}: Нет фактического исхода.")
                            coeff_1 = "Нет фактического исхода. Приняты коэфф: 0"
                            coeff_2 = "0"
                    except Exception as e:
                        print(
                            f"Возможно, в этом матче отсутствуют некоторые данные, например: угловые.: {e}.")

                    # if red_card_1 != "0" and score_t_1 > score_t_2 and float(coeff_2) > 5:
                    if red_card_1 != "0" and score_t_1 != score_t_2:

                        # Добавляем данные о матче в список
                        info.append({
                            f"Матч {index + 1}": two_team,
                            "Красные карточки": [red_card_1, red_card_2],
                            "Счёт": score.replace(":", " - "),
                            "Время матча": match_time_2.replace("\n", " ").replace("   ", " ").strip(),
                            "Угловые": [corner_1, corner_2],
                            "Удары по воротам": [kick_on_gate_1, kick_on_gate_2],
                            "Удары в створ": [kick_on_target_1, kick_on_target_2],
                            "Коэффициенты на победу": [coeff_1, coeff_2]
                        })
                    # elif red_card_2 != "0" and score_t_2 > score_t_1 and float(coeff_1) > 5:
                    elif red_card_2 != "0" and score_t_2 != score_t_1:

                        info.append({
                            f"Матч {index + 1}": two_team,
                            "Красные карточки": [red_card_1, red_card_2],
                            "Счёт": score.replace(":", " - "),
                            "Время матча": match_time_2.replace("\n", " ").replace("   ", " ").strip(),
                            "Угловые": [corner_1, corner_2],
                            "Удары по воротам": [kick_on_gate_1, kick_on_gate_2],
                            "Удары в створ": [kick_on_target_1, kick_on_target_2],
                            "Коэффициенты на победу": [coeff_1, coeff_2]
                        })

                    print(info)

                    # Возвращаемся на предыдущую страницу и обновляем контейнеры
                    driver.back()
                    containers = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CLASS_NAME, "line-event__name-team"))
                    )

            except Exception as e:
                print(f"Ошибка при обработке матча {index + 1}: {e}")

    except Exception as e:
        print(f"Ошибка в процессе обработки матчей: {e}")

    finally:
        driver.quit()
    return info

# if __name__ == "__main__":
#     match_info()

# //////////////////////////////////////////////////////////////////////////////////////

# TODO:   create function for searching data of matches
