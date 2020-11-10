"""Representa a constituição da IPB.

Classes:
    Constituicao
    Capitulo
    Secao
    Artigo
    Paragrafo
    Caput
    Alinea
    Utilitario
"""

import re
import sys
from collections import namedtuple
from operator import attrgetter
import roman
from yattag import Doc


class Constituicao:
    """Representa a constituição, formada por um conjunto de capítulos.

    Attrs:
        capitulos (list[Capitulo]): Conjunto de capítulos da constituição.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Constituicao a partir de um documento XML.

        Args:
            xml (Element): Documento XML com o conteúdo da constituição.
        """

        self.capitulos = []

        for capitulo in xml.findall('capitulo'):
            self.capitulos.append(Capitulo(capitulo))

    def gerar_html(self):
        """Gera a materialização da constituição como documento HTML.

        Returns:
            yattag.doc.Doc: Documento HTML com a constituição.
        """

        titulo = 'Constituição da Igreja Presbiteriana do Brasil'
        preambulo = ('Em nome do Pai, do Filho e do Espírito Santo, nós, legítimos representantes '
                     'da Igreja Cristã Presbiteriana do Brasil, reunidos em Supremo Concílio, '
                     'no ano de 1950, com poderes para reforma da Constituição, investidos de toda '
                     'autoridade para cumprir as resoluções da legislatura de 1946, depositando '
                     'toda nossa confiança na bênção do Deus Altíssimo e tendo em vista a promoção '
                     'da paz, disciplina, unidade e edificação do povo de Cristo, elaboramos, '
                     'decretamos e promulgamos, para glória de Deus, a seguinte Constituição da '
                     'Igreja Presbiteriana do Brasil.')
        capitulos = {'preambulo': 'Preâmbulo',
                     'c1': 'I - Natureza, Governo e Fins da Igreja',
                     'c2': 'II - Organização das Comunidades Locais',
                     'c3': 'III - Membros da Igreja',
                     'c4': 'IV - Oficiais',
                     'c5': 'V - Concílios',
                     'c6': 'VI - Comissões e Outras Organizações',
                     'c7': 'VII - Ordens da Igreja',
                     'cdg': 'Disposições Gerais',
                     'cdt': 'Disposições Transitórias'}

        doc, tag, text, line = Doc().ttl()
        html = {'doc': doc, 'tag': tag, 'text': text, 'line': line}

        doc.asis('<!doctype html>')

        with tag('html', lang='pt-BR', klass='has-navbar-fixed-bottom'):
            with tag('head'):
                doc.stag('meta', charset='utf-8')
                line('title', titulo)
                doc.stag('meta', name='author',
                         content='Igreja Presbiteriana do Brasil')
                doc.stag('meta', name='viewport',
                         content='width=device-width, initial-scale=1')
                doc.stag('link', rel='stylesheet',
                         href='https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css')
                with tag('style'):
                    text('span[data-lang] { font-style: italic; }')
                    text('del { text-decoration: line-through }')
                line('script', '', src='base.js')

            with tag('body'):
                with tag('nav', ('aria-label', 'main navigation'),
                         klass='navbar is-fixed-bottom is-light is-hidden-mobile'
                         ):
                    with tag('div', klass='navbar-menu'):
                        with tag('div', klass='navbar-start'):
                            with tag('div', klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                                line('a', 'Índice', href='#', klass='navbar-link')

                                with tag('div', klass='navbar-dropdown'):
                                    for chave, texto in capitulos.items():
                                        line('a', texto, klass='navbar-item', href=f'#{chave}')
                                        if chave in ('preambulo', 'c7'):
                                            doc.stag('hr', klass='navbar-divider')

                        with tag('div', klass='navbar-end'):
                            with tag('div', klass='navbar-item'):
                                with tag('label', klass='checkbox'):
                                    doc.stag('input', type='checkbox', id='mostrar_versoes')
                                    text(' Apresentar versões obsoletas')

                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', titulo, klass='title is-1 has-text-centered')

                        line('h2', 'Índice', klass='title is-3 has-text-centered is-hidden-tablet')
                        with tag('ul', klass='content is-hidden-tablet'):
                            for chave, texto in capitulos.items():
                                with tag('li'):
                                    line('a', texto, klass='', href=f'#{chave}')

                        with tag('section', id='preambulo', klass='capitulo block'):
                            line('h2', 'Preâmbulo',
                                 klass='title is-3 has-text-centered')
                            line('p', preambulo)

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(html)

        return doc


class Capitulo:
    """Representa um capítulo da constituição, formado por um conjunto de seções.

    Attrs:
        secoes (list[Secao]): Conjunto de seções do capítulo.
        id (str): Identificador do capítulo.
        titulo (str): Título do capítulo.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Capitulo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do capítulo.
        """

        self.secoes = []
        self.id = xml.attrib['id']
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(self, secao))

    def gerar_html(self, html):
        """Adiciona a materialização do capítulo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='capitulo block'):
            if self.id != 'dg' and self.id != 'dt':
                line('h2', f'Capítulo {roman.toRoman(int(self.id))}',
                     klass='title is-3 has-text-centered')

            line('h2', self.titulo, klass='title is-3 has-text-centered')

            for secao in self.secoes:
                secao.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do capítulo para uso em link HTML.

        Returns:
            str: Identificador do capítulo.
        """

        return f'c{self.id}'


class Secao:
    """Representa uma seção de um capítulo, formada por um conjunto de artigos.

    Attrs:
        artigos (list[Artigo]): Conjunto de artigos da seção.
        id (str): Identificador da seção.
        titulo (str): Título da seção.
        pai (Capitulo): Capítulo que contém a seção.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Secao a partir de um fragmento de XML.

        Args:
            pai (Capitulo): Capítulo que contém a seção.
            xml (Element): Fragmento de XML com o conteúdo da seção.
        """

        self.artigos = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None
        self.pai = pai

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))

    def gerar_html(self, html):
        """Adiciona a materialização da seção ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='secao block'):
            if self.titulo is None:
                titulo = 'Única'
                visibilidade = ' is-sr-only'
            else:
                titulo = f'{self.id}ª - {self.titulo}'
                visibilidade = ''

            line('h2', f'Seção {titulo}',
                 klass=f'title is-5 has-text-centered{visibilidade}')

            for artigo in self.artigos:
                artigo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador da seção para uso em link HTML.

        Returns:
            str: Identificador da seção.
        """

        return f'{self.pai.obter_id_html()}_s{self.id}'


class Artigo:
    """Representa um artigo, formado por um conjunto de parágrafos.

    Attrs:
        paragrafos (list[Paragrafo]): Conjunto de parágrafos do artigo.
        id (str): Identificador da seção.
    """
    def __init__(self, xml):
        """Inicia uma instância da classe Artigo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do artigo.
        """

        self.paragrafos = []
        self.id = int(xml.attrib['id'])

        self.paragrafos.append(Caput(self, xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(self, paragrafo))

    def gerar_html(self, html):
        """Adiciona a materialização do artigo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        with tag('div', id=self.obter_id_html(), klass='artigo block'):
            for paragrafo in self.paragrafos:
                paragrafo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do artigo para uso em link HTML.

        Returns:
            str: Identificador do artigo.
        """

        return f'a{self.id}'


class Paragrafo:
    """Representa um parágrafo de um artigo.

    Attrs:
        id (str): Identificador da seção.
        alineas (list[Alineas]): Conjunto de alíneas do parágrafo.
        versoes_texto (): Conjunto de versões do texto do parágrafo.
        pai (Artigo): Artigo que contém o parágrafo.
        vigente (bool): Valor que indica se o parágrafo está vigente.
    """
    def __init__(self, pai, xml, caput=False):
        """Inicia uma instância da classe Paragrafo a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o parágrafo.
            xml (Element): Fragmento de XML com o conteúdo do parágrafo.
            caput (bool, optional): Valor que indica se o parágrafo é o caput do artigo. Padrão: False.
        """

        self.id = 0 if caput else int(xml.attrib['id'])
        self.alineas = []
        self.versoes_texto = []
        self.pai = pai
        self.vigente = True

        for versao in xml.findall('texto'):
            texto = versao.text
            instrumento = versao.attrib['instrumento'] if 'instrumento' in versao.attrib else None
            ordem = int(versao.attrib['ordem']
                        ) if 'ordem' in versao.attrib else 1

            if any(v.ordem == ordem for v in self.versoes_texto):
                print(f'{Utilitario.ERRO}Erro{Utilitario.ENDC}')
                print(f'* Texto com ordem repetida: {texto}')
                sys.exit(1)

            Utilitario.verificar_pontuacao(texto)

            self.vigente = self.vigente and texto != 'Revogado.'
            self.versoes_texto.append(
                Utilitario.VersaoTexto(texto, instrumento, ordem))

        self.versoes_texto = sorted(
            self.versoes_texto, key=attrgetter('ordem'))

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(self, alinea))

    def gerar_html(self, html):
        """Adiciona a materialização do parágrafo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        if self.id == 0:
            tipo = 'caput'
            terminal = 'º' if self.pai.id < 10 else '.'
            rotulo = f'Art. {self.pai.id}{terminal}'
        else:
            tipo = 'paragrafo'
            if len(self.pai.paragrafos) > 2:
                rotulo = f'§ {self.id}º.'
            else:
                rotulo = 'Parágrafo único.'

        numero_versoes = len(self.versoes_texto)

        with tag('p', id=self.obter_id_html(), klass=f'{tipo} content'):
            for indice, versao in enumerate(self.versoes_texto, start=1):
                versao_vigente = indice == numero_versoes

                classes = f'versao{"" if versao_vigente else " obsoleta is-hidden"}'

                if versao.instrumento is not None:
                    with tag('span', ('data-instrumento', versao.instrumento), klass=classes):
                        Paragrafo.__gerar_versao(html, versao_vigente, rotulo, versao.texto)
                else:
                    with tag('span', klass=classes):
                        Paragrafo.__gerar_versao(html, versao_vigente, rotulo, versao.texto)

            for alinea in self.alineas:
                alinea.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do parágrafo para uso em link HTML.

        Returns:
            str: Identificador do parágrafo.
        """

        return f'{self.pai.obter_id_html()}_p{self.id}'

    @staticmethod
    def __gerar_versao(html, vigente, rotulo, texto):
        """Adiciona a materialização da versão do texto do parágrafo ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
            vigente (bool): Valor que indica se a versão é vigente.
            rotulo (str): Rótulo do parágrafo.
            texto (str): Texto do parágrafo na versão.
        """

        doc = html['doc']
        tag = html['tag']
        line = html['line']

        if not vigente:
            with tag('del'):
                line('strong', rotulo)
                doc.asis(f' {Utilitario.processar_texto(texto)}')

            doc.stag('br')
        else:
            line('strong', rotulo)
            doc.asis(f' {Utilitario.processar_texto(texto)}')


class Caput(Paragrafo):
    """Representa o caput de um artigo."""

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Caput a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o caput.
            xml (Element): Fragmento de XML com o conteúdo do caput.
        """

        super().__init__(pai, xml, caput=True)

    def gerar_html(self, html):
        """Adiciona a materialização do caput ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        super().gerar_html(html)


class Alinea:
    """Representa uma alínea de um parágrafo.

    Attrs:
        id (str): Identificador da alínea.
        texto (str): Texto da alínea.
        pai (Paragrafo): Parágrafo que contém a alínea.
    """
    def __init__(self, pai, xml):
        """Inicia uma instância da classe Alinea a partir de um fragmento de XML.

        Args:
            pai (Paragrafo): Parágrafo que contém a alínea.
            xml (Element): Fragmento de XML com o conteúdo da alínea.
        """

        self.id = xml.attrib['id']
        self.texto = xml.text
        self.pai = pai

        Utilitario.verificar_pontuacao(self.texto)

    def gerar_html(self, html):
        """Adiciona a materialização da alínea ao documento HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        doc = html['doc']
        tag = html['tag']

        doc.stag('br')
        with tag('span', id=self.obter_id_html()):
            doc.asis(f'{self.id}) {Utilitario.processar_texto(self.texto)}')

    def obter_id_html(self):
        """Obtém o identificador da alínea para uso em link HTML.

        Returns:
            str: Identificador da alínea.
        """

        return f'{self.pai.obter_id_html()}_{self.id}'


class Utilitario:
    """Define métodos e atributos utilitários para o tratamento da constituição."""

    VersaoTexto = namedtuple('VersaoTexto', 'texto instrumento ordem')

    ALERTA = '\033[33m'
    ERRO = '\033[31m'
    ENDC = '\033[0m'

    @staticmethod
    def verificar_pontuacao(texto):
        """Verifica a presença de pontuação ao fim de um texto.

        Args:
            texto (str): Texto que deve terminar com pontuação.
        """

        if not texto.endswith(tuple([';', '.', ':'])):
            print(f'{Utilitario.ALERTA}Alerta{Utilitario.ENDC}')
            print(f'* Texto sem terminal: {texto}')

    @staticmethod
    def processar_texto(texto):
        """Processa um texto marcando referências e termos latinos.

        Args:
            texto (str): Texto com referências e termos latinos.

        Returns:
            str: Texto com referências e termos latinos marcados.
        """

        return Utilitario.marcar_referencias(Utilitario.marcar_termos_latinos(texto))

    @staticmethod
    def marcar_referencias(texto):
        """Identifica referências em um texto e as marca como links HTML.

        Args:
            texto (str): Texto com referências.

        Returns:
            str: Texto com referências marcadas.
        """

        return re.sub(r'art\. (\d{1,3})(º)?', r'<a href="#a\1">art. \1\2</a>', texto)

    @staticmethod
    def marcar_termos_latinos(texto):
        """Identifica termos latinos em um texto e os marca para destaque.

        Args:
            texto (str): Texto com termos latinos.

        Returns:
            str: Texto com termos latinos marcados.
        """

        termos = ['ex officio', 'in fine', 'ad referendum', 'quorum']
        return re.sub(f"({'|'.join(termos)})", r'<span data-lang="latim">\1</span>', texto)
