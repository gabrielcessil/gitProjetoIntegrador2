import PySimpleGUI as psg
import VolumeMixer as mm
import ColetorUSB as cusb
import time


class Module:
    def __init__(self, appName="", fisicalIndex=-1):
        self.AppName = appName
        self.FisicalIndex = fisicalIndex

    def getAppName(self):
        return self.AppName

    def getFisicalIndex(self):
        return self.FisicalIndex

    def setAppName(self, name):
        self.appName = name

    def setFisicalIndex(self, index):
        self.FisicalIndex = index


class ModulesCollection:
    def __init__(self):
        self.Modules = []

    def AddModulo(self, appName, fisicalIndex):
        self.Modules.append(Module(appName, fisicalIndex))

    def CreateCollection(self, DicValues):
        self.Modules = []
        for elem, index in zip(DicValues, range(len(DicValues))):
            self.AddModulo(DicValues[elem], index)

    def GetCollection(self):
        return self.Modules

    def GetNomeFonte(self, moduleIndex):
        for module in self.Modules:
            if moduleIndex == module.getFisicalIndex():
                return module.getAppName()
        return []


class ModMixerGUI:
    def __init__(self):
        self.usbColetor = cusb.ColetorUSB()
        self.mixer = mm.Mixer("User")
        self.modules = ModulesCollection()
        self.numerModulos = 0
        self.refreshTimeoutTime = 5
        self.NumeroMaximoModulos = 3
        self.setAppNames()

    def AtualizaNumeroModulos(self, nModules):
        self.numerModulos = nModules

    def getNumeroModulos(self):
        return self.numerModulos

    def getApplicationsName(self):
        nomes = self.mixer.GetNomeFontes()
        return nomes

    def AtualizaEscolhasIndex(self, DicValues):
        self.modules.CreateCollection(DicValues)

    def setVisibles(self):
        if self.EhMixerAtivado():
            for index in range(self.NumeroMaximoModulos):
                if index < self.getNumeroModulos():
                    isVisible = True
                else:
                    isVisible = False

                self.win["volumeBar" + str(index)].Update(visible=isVisible)
                self.win["apps_List" + str(index)].Update(visible=isVisible)
                self.win["mixer_line" + str(index)].Update(visible=isVisible)

    def CriaLayoutMixerAtivado(self):
        nomes_app = self.getApplicationsName()
        nomes_app.append("none")

        layout = []
        title_line = psg.Text(
            "Select applications", font="Arial 15", justification="center"
        )
        layout.append([title_line])

        # Gera menu para cada possivel mixer
        for index in range(self.NumeroMaximoModulos):
            mixer_line = psg.Text(
                "mixer [" + str(index) + "]",
                key="mixer_line" + str(index),
                font="Arial 15",
                justification="left",
                visible=False,
            )

            layout.append(
                [
                    psg.Combo(nomes_app, key="apps_List" + str(index), visible=False),
                    mixer_line,
                ]
            )

            layout.append(
                [
                    psg.ProgressBar(
                        max_value=1.2,
                        orientation="h",
                        bar_color=("green", "grey"),
                        style="vista",
                        size=(22, 5),
                        key="volumeBar" + str(index),
                        visible=False,
                    )
                ]
            )
        layout.append([psg.Button("Refresh APP's list"), psg.Button("Apply changes")])

        return layout

    def CriaLayoutMixerDesativado(self):
        layout = []
        mixer_line = psg.Text(
            "Please, connect the ModMixers modules",
            font="Arial 15",
            justification="center",
        )
        layout.append([mixer_line])

        return layout

    def CriaLayout(self):
        if self.EhMixerAtivado():
            layout = self.CriaLayoutMixerAtivado()
        else:
            layout = self.CriaLayoutMixerDesativado()
        return layout

    def CriaJanela(self):

        # Cria layouts
        layout = self.CriaLayout()
        # Cria novo objeto de janela
        self.win = psg.Window("ModMixer", layout, finalize=True)

    def EhFechamento(self, event):
        if event == psg.WIN_CLOSED or event == "None":
            return True
        else:
            return False

    def setAppNames(self):
        self.AppNames = self.getApplicationsName()

    # Verifica se existem mixers conectados
    def EhMixerAtivado(self):
        if self.getNumeroModulos() > 0:
            return True
        else:
            return False

    def AtualizaBarrasTela(self):
        # Para cada fonte selecianada no menu:
        for module in self.modules.GetCollection():

            # Coleta o volume dessa fonte
            volFonte = self.mixer.GetVolume(module.getAppName())

            # Atualiza a barra com esse valor de volume
            progress_bar = self.win["volumeBar" + str(module.getFisicalIndex())]
            progress_bar.UpdateBar(volFonte)

    def AtualizaListaApps(self):

        nomes_app = self.getApplicationsName()
        for index in range(self.NumeroMaximoModulos):
            # Atualiza nomes dos aplicativos: (atenção no 'apenas' mudar a ordem e ja alterar tudo)
            self.win["apps_List" + str(index)].update(value="", values=nomes_app)

    def FechaJanela(self):
        self.win.close()

    # Uma janela ja deve ter sido criada
    def AguardaModules(self, Sinais):

        # Caso a janela tenha sido criada para o sistema sem som
        if not self.EhMixerAtivado():

            # Refaz a janela
            self.FechaJanela()
            self.CriaJanela()

            # Aguarda Fontes de som
            while not self.EhMixerAtivado():
                print("Aguardando")
                # Captura entradas ate que identifique a existencia de um mixer fisico
                Sinais = self.usbColetor.CapturaComando()
                time.sleep(0.001)

            # Fecha a janela para o sistema sem som, para que possa ser substituida
            self.FechaJanela()
            self.CriaJanela()

        return Sinais

    def LeituraDeJanela(self, timoutOn=False):
        if timoutOn:
            event, values = self.win.read(timeout=self.refreshTimeoutTime)
        else:
            event, values = self.win.read()
        return [event, values]

    def InterpretaSinal_ModuleIndex(self, moduleIndex_signal):
        try:
            moduleIndex = int(moduleIndex_signal)
        except:
            moduleIndex = -1

        # Traduz o index do mixer fisico para um nome de fonte
        nomeFonte = self.modules.GetNomeFonte(moduleIndex)
        print("NOME FONTE:", nomeFonte, ", MIXER INDEX: ", moduleIndex)
        # Mixer responde quais fontes pertencem este nome
        fontes = self.mixer.GetFontePorNome(nomeFonte)

        return fontes

    def InterpretaSinal_Percentual(self, percentual_signal):
        try:
            percentual = float(percentual_signal)
        except:
            raise Exception(
                "Erro de comunicacao <Sinal desconhecido>: percentual = "
                + percentual_signal
            )
        return percentual

    def InterpretaSinal_Cabecalho(self, cabecalho_signal):
        if cabecalho_signal == "F":
            cabecalho = self.mixer.Cabecalhos["Fonte"]
        elif cabecalho_signal == "G":
            cabecalho = self.mixer.Cabecalhos["Geral"]
        else:
            cabecalho = self.mixer.Cabecalhos["Iddle"]
        return cabecalho

    def InterpretaSinais(self, Sinais):

        SinaisInterpretados = []
        for [cabecalho_signal, moduleIndex_signal, percentual_signal] in Sinais:

            comando = self.InterpretaSinal_Cabecalho(cabecalho_signal)
            percentual = self.InterpretaSinal_Percentual(percentual_signal)
            fontes = self.InterpretaSinal_ModuleIndex(moduleIndex_signal)

            SinaisInterpretados.append([comando, fontes, percentual])

        return SinaisInterpretados

    def OperaEntradasJanela(self, event, values):
        print("evento::", event)
        if self.EhFechamento(event):
            self.win.close()
            quit()
        elif event == "Apply changes":
            print("Apply changes")
            # Altera valores de index e nome de app conforme definido no menu
            self.AtualizaEscolhasIndex(values)
        elif event == "Refresh APP's list":
            print("Refresh APP's list")
            self.AtualizaListaApps()

    def loop(self):

        # Inicia escuta por mixers fisicos para criar layout
        Sinais, nModules = self.usbColetor.CapturaComando()

        self.AtualizaNumeroModulos(nModules)

        # Cria janela com layout inicial
        self.CriaJanela()
        # Aguarda o sistema identificar mixers fisicos, e exibe tela de espera
        Sinais = self.AguardaModules(Sinais)

        # Retira da janela os menus de mixers desconectados
        self.setVisibles()

        while True:
            print("\n")
            # Traduz esses sinais para comandos conhecidos (MIXER.INDEX -> nomeAPP)
            SinaisInterpretados = self.InterpretaSinais(Sinais)

            # Espera leitura eventos e valores de entrada
            [event, values] = self.LeituraDeJanela(timoutOn=True)

            self.OperaEntradasJanela(event, values)

            self.AtualizaBarrasTela()

            # Realiza as operacoes indicadas pelos comandos traduzidos
            self.mixer.OperaComandos(SinaisInterpretados)

            # Recebe comandos dos mixers fisicos pelo usb (MIXER.INDEX)
            Sinais, nModules = self.usbColetor.CapturaComando()
            self.AtualizaNumeroModulos(nModules)

            # Retira da janela os menus de mixers desconectados
            self.setVisibles()

            # Aguarda o sistema identificar Modules conectados, e exibe tela de espera
            Sinais = self.AguardaModules(Sinais)


# """

# DESEJADO:

# ELE PRECISA ATUALIZAR A ESCOLHA DE INDEX SOMENTE APOS O CLIQUE
# AS OPCOES DE APP ATUALIZAM COM REFRESH OU A CADA 100ms
# AS BARRA DE VOLUME ATUALIZAM COM ALTA FREQUENCIA
# OS MIXERS APARECEM CONFORME "SOLITICADOS" PELO VOLUMEMIXER (nao pelo numero de abas)

# USB (Captura sinal (ModuleIndex))
# GUI(MIXER.INDEX -> nomeAPP)
# VolumeModule (nomeAPP --ProcuraPeloNome-> fonte -> Atuacao na fonte)


# BUG, SE EFETUA MUDANCA NAS BARRAS E FECHA SEM SALVAR ELE CRASHA
