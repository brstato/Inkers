# Base de Conhecimento Oficial do Flet
Este documento contém a documentação atualizada do framework Flet para Python.

## Referência de URL: https://flet.dev/docs/guides/python/getting-started

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/layout

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/state-management

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/routing

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/user-controls

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/colors

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

## Referência de URL: https://flet.dev/docs/guides/python/keyboard-shortcuts

# Introduction

Flet is a framework that allows building web, desktop and mobile applications in Python without prior experience in frontend development.

## Flet app example[#](#flet-app-example "Permanent link")

Below is a simple "Counter" app, with a text field and two buttons to increment and decrement the counter value:

counter.py

```
import flet as ft

def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    input = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100)

    def minus_click(e):
        input.value = str(int(input.value) - 1)

    def plus_click(e):
        input.value = str(int(input.value) + 1)

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.IconButton(ft.Icons.REMOVE, on_click=minus_click),
                input,
                ft.IconButton(ft.Icons.ADD, on_click=plus_click),
            ],
        )
    )

ft.run(main)
```

To run the app, [install `flet`](getting-started/installation/):

```
pip install 'flet[all]'
```

then launch the app:

```
flet run counter.py
```

This will open the app in a native OS window - what a nice alternative to Electron! 🙂

[![](assets/getting-started/counter-app/macos.png)](assets/getting-started/counter-app/macos.png)

To run the same app as a web app use `--web` option with `flet run` command:

```
flet run --web counter.py
```

[![](assets/getting-started/counter-app/safari.png)](assets/getting-started/counter-app/safari.png)

---

