# IDENTIFICAÇÃO DO ESTUDANTE:
# Preencha seus dados e leia a declaração de honestidade abaixo. NÃO APAGUE
# nenhuma linha deste comentário de seu código!
#
#    Nome completo: Arthur Romani Inacio de Souza
#    Matrícula: 202305764
#    Turma: CC3M
#    Email: romaniarthur280104@gmail.com
#
# DECLARAÇÃO DE HONESTIDADE ACADÊMICA:
# Eu afirmo que o código abaixo foi de minha autoria. Também afirmo que não
# pratiquei nenhuma forma de "cola" ou "plágio" na elaboração do programa,
# e que não violei nenhuma das normas de integridade acadêmica da disciplina.
# Estou ciente de que todo código enviado será verificado automaticamente
# contra plágio e que caso eu tenha praticado qualquer atividade proibida
# conforme as normas da disciplina, estou sujeito à penalidades conforme
# definidas pelo professor da disciplina e/ou instituição.


# Imports permitidos (não utilize nenhum outro import!):
import sys
import math
import base64
import tkinter
from io import BytesIO
from PIL import Image as PILImage


# Classe Imagem:
class Imagem:
    def __init__(self, largura, altura, pixels):
        self.largura = largura
        self.altura = altura
        self.pixels = pixels

    def kernel_desfoque_caixa(n):
        return [[1 / (n * n) for _ in range(n)] for _ in range(n)]

    def correlacionar(self, kernel):
        resultado = Imagem.nova(self.largura, self.altura)
        ksize = len(kernel)
        offset = ksize // 2
        for y in range(self.altura):
            for x in range(self.largura):
                total = 0
                for ky in range(ksize):
                    for kx in range(ksize):
                        px = x - offset + kx
                        py = y - offset + ky
                        if 0 <= px < self.largura and 0 <= py < self.altura:
                            total += self.get_pixel(px, py) * kernel[ky][kx]
                resultado.set_pixel(x, y, total)
        return resultado

    def get_pixel(self, x, y):
        if 0 <= x < self.largura and 0 <= y < self.altura:    # Verificar se esta dentro da imagem
            # calcula o indice do pixel na lista de pixels
            indice_pixel = y * self.largura + x
            return self.pixels[indice_pixel]  # retorna o valor do pixel
        else:
            return None  # se as cordenadas estiverem fora dos limites retorna none

    def set_pixel(self, x, y, c):
        if 0 <= x < self.largura and 0 <= y < self.altura:  # Verificar se esta dentro da imagem
            # calcula o indice do pixel na lista de pixels
            indice_pixel = y * self.largura + x
            self.pixels[indice_pixel] = c  # define o valor do pixel
        else:
            pass  # se as cordenadas estiverem fora dos limites passa sem fazer nada

    def aplicar_por_pixel(self, func):
        resultado = Imagem.nova(self.largura, self.altura)
        for x in range(resultado.largura):
            for y in range(resultado.altura):
                cor = self.get_pixel(x, y)
                nova_cor = func(cor)
                resultado.set_pixel(x, y, nova_cor)
        return resultado

    def invertida(self):
        return self.aplicar_por_pixel(lambda c: 255 - c)

    def borrada(self, n):
        kernel = Imagem.kernel_desfoque_caixa(n)
        resultado = self.correlacionar(kernel)
        # Garantir que os valores estejam no intervalo [0, 255]
        for i in range(resultado.largura * resultado.altura):
            resultado.pixels[i] = min(max(round(resultado.pixels[i]), 0), 255)
        return resultado

    def focada(self, n):
        # Primeiro, calculamos a versão borrada da imagem usando o kernel de desfoque de caixa
        img_borrada = self.borrada(n)
        # Agora, construímos o kernel para a máscara de não nitidez
        kernel_nitidez = [
            [-1, -1, -1],
            [-1, 8, -1],
            [-1, -1, -1]
        ]
        # Aplicamos a correlação com o kernel de máscara de não nitidez
        img_nitida = self.correlacionar(kernel_nitidez)
        # Retornamos a imagem nítida
        return img_nitida

    def bordas(self):
       # Kernel Kx
        Kx = [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ]

        # Kernel Ky
        Ky = [
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ]

        # Correlacionar a imagem com os kernels Kx e Ky
        Ox = self.correlacionar(Kx)
        Oy = self.correlacionar(Ky)

        # Calcular a magnitude das derivadas
        resultado = Imagem.nova(self.largura, self.altura)
        for x in range(self.largura):
            for y in range(self.altura):
                magnitude = math.sqrt(Ox.get_pixel(
                    x, y) ** 2 + Oy.get_pixel(x, y) ** 2)
                # Garantir que os valores estejam no intervalo [0, 255]
                resultado.set_pixel(x, y, min(max(round(magnitude), 0), 255))

        return resultado

    # Abaixo deste ponto estão utilitários para carregar, salvar e mostrar
    # as imagens, bem como para a realização de testes. Você deve ler as funções
    # abaixo para entendê-las e verificar como funcionam, mas você não deve
    # alterar nada abaixo deste comentário.
    #
    # ATENÇÃO: NÃO ALTERE NADA A PARTIR DESTE PONTO!!! Você pode, no final
    # deste arquivo, acrescentar códigos dentro da condicional
    #
    #                 if __name__ == '__main__'
    #
    # para executar testes e experiências enquanto você estiver executando o
    # arquivo diretamente, mas que não serão executados quando este arquivo
    # for importado pela suíte de teste e avaliação.
    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('altura', 'largura', 'pixels'))

    def __repr__(self):
        return "Imagem(%s, %s, %s)" % (self.largura, self.altura, self.pixels)

    @classmethod
    def carregar(cls, nome_arquivo):
        """
        Carrega uma imagem do arquivo fornecido e retorna uma instância dessa
        classe representando essa imagem. Também realiza a conversão para tons
        de cinza.

        Invocado como, por exemplo:
           i = Imagem.carregar('test_images/cat.png')
        """
        with open(nome_arquivo, 'rb') as guia_para_imagem:
            img = PILImage.open(guia_para_imagem)
            img_data = img.getdata()
            if img.mode.startswith('RGB'):
                pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                          for p in img_data]
            elif img.mode == 'LA':
                pixels = [p[0] for p in img_data]
            elif img.mode == 'L':
                pixels = list(img_data)
            else:
                raise ValueError('Modo de imagem não suportado: %r' % img.mode)
            l, a = img.size
            return cls(l, a, pixels)

    @classmethod
    def nova(cls, largura, altura):
        """
        Cria imagens em branco (tudo 0) com a altura e largura fornecidas.

        Invocado como, por exemplo:
            i = Imagem.nova(640, 480)
        """
        return cls(largura, altura, [0 for i in range(largura * altura)])

    def salvar(self, nome_arquivo, modo='PNG'):
        """
        Salva a imagem fornecida no disco ou em um objeto semelhante a um arquivo.
        Se o nome_arquivo for fornecido como uma string, o tipo de arquivo será
        inferido a partir do nome fornecido. Se nome_arquivo for fornecido como
        um objeto semelhante a um arquivo, o tipo de arquivo será determinado
        pelo parâmetro 'modo'.
        """
        saida = PILImage.new(mode='L', size=(self.largura, self.altura))
        saida.putdata(self.pixels)
        if isinstance(nome_arquivo, str):
            saida.save(nome_arquivo)
        else:
            saida.save(nome_arquivo, modo)
        saida.close()

    def gif_data(self):
        """
        Retorna uma string codificada em base 64, contendo a imagem
        fornecida, como uma imagem GIF.

        Função utilitária para tornar show_image um pouco mais limpo.
        """
        buffer = BytesIO()
        self.salvar(buffer, modo='GIF')
        return base64.b64encode(buffer.getvalue())

    def mostrar(self):
        """
        Mostra uma imagem em uma nova janela Tk.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            # Se Tk não foi inicializado corretamente, não faz mais nada.
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        # O highlightthickness=0 é um hack para evitar que o redimensionamento da janela
        # dispare outro evento de redimensionamento (causando um loop infinito de
        # redimensionamento). Para maiores informações, ver:
        # https://stackoverflow.com/questions/22838255/tkinter-canvas-resizing-automatically
        tela = tkinter.Canvas(toplevel, height=self.altura,
                              width=self.largura, highlightthickness=0)
        tela.pack()
        tela.img = tkinter.PhotoImage(data=self.gif_data())
        tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        def ao_redimensionar(event):
            # Lida com o redimensionamento da imagem quando a tela é redimensionada.
            # O procedimento é:
            #  * converter para uma imagem PIL
            #  * redimensionar aquela imagem
            #  * obter os dados GIF codificados em base 64 (base64-encoded GIF data)
            #    a partir da imagem redimensionada
            #  * colocar isso em um label tkinter
            #  * mostrar a imagem na tela
            nova_imagem = PILImage.new(
                mode='L', size=(self.largura, self.altura))
            nova_imagem.putdata(self.pixels)
            nova_imagem = nova_imagem.resize(
                (event.width, event.height), PILImage.NEAREST)
            buffer = BytesIO()
            nova_imagem.save(buffer, 'GIF')
            tela.img = tkinter.PhotoImage(
                data=base64.b64encode(buffer.getvalue()))
            tela.configure(height=event.height, width=event.width)
            tela.create_image(0, 0, image=tela.img, anchor=tkinter.NW)

        # Por fim, faz o bind da função para que ela seja chamada quando a tela
        # for redimensionada:
        tela.bind('<Configure>', ao_redimensionar)
        toplevel.bind('<Configure>', lambda e: tela.configure(
            height=e.height, width=e.width))

        # Quando a tela é fechada, o programa deve parar
        toplevel.protocol('WM_DELETE_WINDOW', tk_root.destroy)


# Não altere o comentário abaixo:
# noinspection PyBroadException
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()

    def refaz_apos():
        tcl.after(500, refaz_apos)

    tcl.after(500, refaz_apos)
except:
    tk_root = None

WINDOWS_OPENED = False

if __name__ == '__main__':
    # O código neste bloco só será executado quando você executar
    # explicitamente seu script e não quando os testes estiverem
    # sendo executados. Este é um bom lugar para gerar imagens, etc.
    img_original = Imagem.carregar('bluegill.png')  # Pega a image do peixe
    imgInvertida = img_original.invertida()  # inverte os pixels

    print(imgInvertida.pixels)  # exibe os pixels invertidos

    imgInvertida.salvar('bluegillresultado.png')

    imgInvertida.mostrar()  # exibe os pixels invertidos

    # Carregue a imagem
    img_original = Imagem.carregar('pigbird.png')

    # Defina o kernel
kernel = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]
# Aplique a correlação
img_correlacionada = img_original.correlacionar(kernel)
# Salve a imagem resultante
img_correlacionada.salvar('pigbird_correlacionada.png')
# Exiba a imagem
img_correlacionada.mostrar()
# Carregar a imagem
img_original = Imagem.carregar('cat.png')

# Aplicar o desfoque de caixa com um kernel de tamanho 5
img_borrada = img_original.borrada(5)

# Salvar o resultado como uma imagem PNG
img_borrada.salvar('catresultado.png')
# mostrar a imagem borrada
img_borrada.mostrar()

# Carregar a imagem
img_original = Imagem.carregar('python.png')

# Aplicar o filtro de nitidez com um kernel de tamanho 11
img_nitida = img_original.focada(3)

# Salvar o resultado como uma imagem PNG
img_nitida.salvar('pythonresultado.png')

# Mostrar a imagem nitida
img_nitida.mostrar()

# Carregar a imagem
img_original = Imagem.carregar('construct.png')

# Aplicar o detector de bordas
img_bordas = img_original.bordas()

# Salvar o resultado como uma imagem PNG
img_bordas.salvar('constructresultado.png')

# Mostrar a imagem de bordas
img_bordas.mostrar()
pass

# O código a seguir fará com que as janelas de Imagem.mostrar
# sejam exibidas corretamente, quer estejamos executando
# interativamente ou não:
if WINDOWS_OPENED and not sys.flags.interactive:
    tk_root.mainloop()
