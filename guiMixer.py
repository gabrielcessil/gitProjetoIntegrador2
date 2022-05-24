import PySimpleGUI as psg
import VolumeMixer as mm
import ColetorUSB as cusb
import time


class ModMixerGUI:
    def __init__(self):
        self.usbColetor = cusb.ColetorUSB()
        self.mixer = mm.Mixer("User")
        self.Mixers_NameAndIndex = []  # Trocar por classe
        self.NumeroMixers = 0
        self.refreshTimeoutTime = 5
        self.NumeroMaximoMixers = 3
        self.setAppNames()

    # Usa a mensagem recebida para determinar o numero de mixers
    # Este metodo pode ser vinculado com alguma mensagem recebida do master
    def AtualizaNumeroMixers(self, nMixers):
        self.NumeroMixers = nMixers

    def GetNumeroMixers(self):  # colocar na nova classe
        return self.NumeroMixers

    def GetNomeFonte(self, mixerIndex):  # colocar na nova classe
        for mixerNameAndIndex in self.Mixers_NameAndIndex:
            if mixerIndex == mixerNameAndIndex[1]:
                return mixerNameAndIndex[0]
        return []

    def getApplicationsName(self):
        nomes = self.mixer.GetNomeFontes()
        return nomes

    def AtualizaEscolhasIndex(self, DicValues):
        self.Mixers_NameAndIndex = []
        for elem, index in zip(DicValues, range(len(DicValues))):
            self.Mixers_NameAndIndex.append([DicValues[elem], index])

    def setVisibles(self):
        if self.EhMixerAtivado():
            for index in range(self.NumeroMaximoMixers):
                if index < self.GetNumeroMixers():
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
        for index in range(self.NumeroMaximoMixers):
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
        if event == psg.WIN_CLOSED or event == "Exit":
            return True
        else:
            return False

    def setAppNames(self):
        self.AppNames = self.getApplicationsName()

    # Verifica se existem mixers conectados
    def EhMixerAtivado(self):
        if self.GetNumeroMixers() > 0:
            return True
        else:
            return False

    def AtualizaBarrasTela(self):
        # Para cada fonte selecianada no menu:
        for fonte in self.Mixers_NameAndIndex:
            # MUDAR PARA CLASSE E USAR GET
            fonteName = fonte[0]
            fonteIndex = fonte[1]

            # Coleta o volume dessa fonte
            volFonte = self.mixer.GetVolume(fonteName)
            # Atualiza a barra com esse valor de volume
            progress_bar = self.win["volumeBar" + str(fonteIndex)]
            progress_bar.UpdateBar(volFonte)

    def AtualizaListaApps(self):

        nomes_app = self.getApplicationsName()
        for index in range(self.NumeroMaximoMixers):
            # Atualiza nomes dos aplicativos: (atenção no 'apenas' mudar a ordem e ja alterar tudo)
            self.win["apps_List" + str(index)].update(value="", values=nomes_app)

    def FechaJanela(self):
        self.win.close()

    # Uma janela ja deve ter sido criada
    def AguardaMixers(self, Sinais):

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

        if self.EhFechamento(event):
            quit()
        return [event, values]

    def exibeFontes(self):
        print("Fontes: ")
        for fonte in self.Mixers_NameAndIndex:
            print(fonte[1], fonte[0])

    def InterpretaSinal_MixerIndex(self, mixerIndex_signal):
        try:
            mixerIndex = int(mixerIndex_signal)
        except:
            mixerIndex = -1

        # Traduz o index do mixer fisico para um nome de fonte
        nomeFonte = self.GetNomeFonte(mixerIndex)
        print("NOME FONTE:", nomeFonte, ", MIXER INDEX: ", mixerIndex)
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
        for [cabecalho_signal, mixerIndex_signal, percentual_signal] in Sinais:

            comando = self.InterpretaSinal_Cabecalho(cabecalho_signal)
            percentual = self.InterpretaSinal_Percentual(percentual_signal)
            fontes = self.InterpretaSinal_MixerIndex(mixerIndex_signal)

            SinaisInterpretados.append([comando, fontes, percentual])

        return SinaisInterpretados

    def loop(self):

        # Inicia escuta por mixers fisicos para criar layout
        Sinais, nMixers = self.usbColetor.CapturaComando()

        self.AtualizaNumeroMixers(nMixers)

        # Cria janela com layout inicial
        self.CriaJanela()
        # Aguarda o sistema identificar mixers fisicos, e exibe tela de espera
        Sinais = self.AguardaMixers(Sinais)

        # Retira da janela os menus de mixers desconectados
        self.setVisibles()

        while True:
            print("\n")
            # Traduz esses sinais para comandos conhecidos (MIXER.INDEX -> nomeAPP)
            SinaisInterpretados = self.InterpretaSinais(Sinais)

            # Espera leitura eventos e valores de entrada
            [event, values] = self.LeituraDeJanela(timoutOn=True)

            if event == "Apply changes":
                print("Apply changes")
                # Altera valores de index e nome de app conforme definido no menu
                self.AtualizaEscolhasIndex(values)

            elif event == "Refresh APP's list":
                print("Refresh APP's list")
                self.AtualizaListaApps()

            self.AtualizaBarrasTela()

            # Realiza as operacoes indicadas pelos comandos traduzidos
            self.mixer.OperaComandos(SinaisInterpretados)

            # Recebe comandos dos mixers fisicos pelo usb (MIXER.INDEX)

            Sinais, nMixers = self.usbColetor.CapturaComando()
            self.AtualizaNumeroMixers(nMixers)

            # Retira da janela os menus de mixers desconectados
            self.setVisibles()

            # Aguarda o sistema identificar Mixers conectados, e exibe tela de espera
            Sinais = self.AguardaMixers(Sinais)


# """

# DESEJADO:

# ELE PRECISA ATUALIZAR A ESCOLHA DE INDEX SOMENTE APOS O CLIQUE
# AS OPCOES DE APP ATUALIZAM COM REFRESH OU A CADA 100ms
# AS BARRA DE VOLUME ATUALIZAM COM ALTA FREQUENCIA
# OS MIXERS APARECEM CONFORME "SOLITICADOS" PELO VOLUMEMIXER (nao pelo numero de abas)


# BUGS:

# SE ELE INICIA SEM BOTAO, COMO ELE SAI DA TELA DE AGUARDO

# BARRA DE VOLUME NAO ESTA ACOMPANHANDO

# Se ele inicia em tela de 1 mixer, ele vai para 2?

# TIRAR EFEITO DE APAGAR TUDO QUANDO DA REFRESH, GUARDAR ORDEM E COLOCAR NOS DEFAULT
# A OPCAO ESCOLHIDA DEVE PERMANECER


# Os comandos sao dados na ordem de indexacao da GUI
# Apartir desse index -> nome do app -PROCURA-> index do sistema


# USAR O NOME DO APP INVES DO INDICE DA FONTE! O indice muda, nao adianta salvar


# USB (Captura sinal (MixerIndex))
# GUI(MIXER.INDEX -> nomeAPP)
# VolumeMixer (nomeAPP --ProcuraPeloNome-> fonte -> Atuacao na fonte)
