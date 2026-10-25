import flet as ft

from screens.welcome import welcome_screen


def main(page: ft.Page):
    page.title = "FlowShelter"
    page.padding = 0
    page.bgcolor = "#F5F7F2"

    page.views.append(welcome_screen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)
