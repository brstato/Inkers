import flet as ft
import flet.canvas as cv
import base64
from io import BytesIO
from PIL import Image, ImageDraw


class SignaturePad(ft.Container):
    def __init__(self, height=200, width=None, stroke_color=ft.Colors.BLACK, stroke_width=3, visible:bool=False):
        super().__init__()
        self.content = ft.Column()
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.shapes = []  # Lista para armazenar os traços (paths)
        self.current_path = None # Traço atual sendo desenhado
        self.visible = visible
        self.shapes = []
        self.draw_data = []
        self.current_points = []
        
        # Canvas onde o desenho acontece
        self.canvas = cv.Canvas(
            shapes=self.shapes,
            content=ft.GestureDetector(
                on_pan_start=self.start_stroke,
                on_pan_update=self.update_stroke,
                on_pan_end=self.end_stroke,
                drag_interval=10, # Otimização para não sobrecarregar
            ),
            expand=True
        )

        # Container visual (borda e fundo)
        self.bgcolor = ft.Colors.WHITE
        self.border = ft.border.all(1, ft.Colors.GREY_400)
        self.border_radius = 10
        self.height = height
        self.width = width
        self.content = self.canvas

    def start_stroke(self, e: ft.DragStartEvent):
        # Inicia um novo caminho (Path) quando o usuário toca na tela
        self.current_path = cv.Path(
            [cv.Path.MoveTo(e.local_x, e.local_y)],
            paint=ft.Paint(
                stroke_width=self.stroke_width,
                style=ft.PaintingStyle.STROKE,
                color=self.stroke_color,
                stroke_cap=ft.StrokeCap.ROUND,
                stroke_join=ft.StrokeJoin.ROUND,
            ),
        )
        self.shapes.append(self.current_path)
        # inicia a lista de pontos do traço atual
        self.current_points = [(e.local_x, e.local_y)]
        self.update()

    def update_stroke(self, e: ft.DragUpdateEvent):
        # Adiciona linhas ao caminho enquanto o usuário arrasta
        if self.current_path:
            self.current_path.elements.append(cv.Path.LineTo(e.local_x, e.local_y))
            # registra também os pontos vetoriais para exportação/rasters
            self.current_points.append((e.local_x, e.local_y))
            self.update()

    def clear(self):
        # Limpa a assinatura
        self.shapes.clear()
        self.draw_data.clear()
        self.current_points = []
        self.current_path = None
        self.update()

    def get_signature_data(self):
        # Retorna os dados vetoriais da assinatura (para salvar no BD)
        # Você pode converter isso para JSON string depois
        return str(self.shapes)
    
    def is_empty(self):
        # considera vazio se não houver dados vetoriais gravados
        return len(self.draw_data) == 0 and len(self.shapes) == 0
    

    def end_stroke(self, e: ft.DragEndEvent):
            # Salva o traço completo na lista principal
            if self.current_points:
                # garante que o ponto final esteja presente
                # alguns eventos de drag_end podem não trazer as coordenadas finais
                try:
                    last = (e.local_x, e.local_y)
                    if self.current_points[-1] != last:
                        self.current_points.append(last)
                except Exception:
                    pass
                self.draw_data.append(self.current_points)
                self.current_points = []
            # finalizar o caminho atual
            self.current_path = None
            self.update()


# No arquivo signaturepad.py
    def export_to_base64(self):
        if self.is_empty():
            return None

        # 1. Define um tamanho fixo e razoável (ex: 400x200 é ótimo para relatórios)
        target_width = 400
        target_height = 200
        
        # Cria imagem RGB com fundo branco
        image = Image.new("RGB", (target_width, target_height), "white")
        draw = ImageDraw.Draw(image)

        for stroke in self.draw_data:
            if len(stroke) > 1:
                draw.line(stroke, fill="black", width=self.stroke_width)
            else:
                x, y = stroke[0]
                r = self.stroke_width / 2
                draw.ellipse((x-r, y-r, x+r, y+r), fill="black")

        # 2. OTIMIZAÇÃO: Salvar em memória comprimindo
        buffered = BytesIO()
        # Salva como PNG otimizado
        image.save(buffered, format="PNG", optimize=True)
        
        # Retorna a string pronta para o banco
        return base64.b64encode(buffered.getvalue()).decode("utf-8")                