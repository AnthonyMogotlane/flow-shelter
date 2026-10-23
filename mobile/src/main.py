import flet as ft


def main(page: ft.Page):
    page.title = "FlowShelter"
    page.padding = 0
    page.bgcolor = "#F5F7F2"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    message = ft.Text(
        "",
        size=16,
        color="#64736A",
        text_align=ft.TextAlign.CENTER,
    )

    def say_hello(e):
        message.value = "We say 'Plan for the days between paydays!;"
        page.update()

    page.add(
        ft.Column(
            [
                ft.Text(
                    "Welcome to FlowShelter",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color="#244B3D",
                    text_align=ft.TextAlign.CENTER,
                ),
                message,
                ft.Button(content="Get started", on_click=say_hello),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
        ),
    )


if __name__ == "__main__":
    ft.run(main)
