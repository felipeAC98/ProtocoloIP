from iputils import *


class IP:
    def __init__(self, enlace):
        """
        Inicia a camada de rede. Recebe como argumento uma implementação
        de camada de enlace capaz de localizar os next_hop (por exemplo,
        Ethernet com ARP).
        """
        self.callback = None
        self.enlace = enlace
        self.enlace.registrar_recebedor(self.__raw_recv)
        self.ignore_checksum = self.enlace.ignore_checksum
        self.meu_endereco = None
        self.tabela = None

    def __raw_recv(self, datagrama):
        dscp, ecn, identification, flags, frag_offset, ttl, proto, \
           src_addr, dst_addr, payload = read_ipv4_header(datagrama)
        if dst_addr == self.meu_endereco:
            # atua como host
            if proto == IPPROTO_TCP and self.callback:
                self.callback(src_addr, dst_addr, payload)
        else:
            # atua como roteador
            next_hop = self._next_hop(dst_addr)
            # TODO: Trate corretamente o campo TTL do datagrama
            self.enlace.enviar(datagrama, next_hop)

    def _next_hop(self, dest_addr):
        # TODO: Use a tabela de encaminhamento para determinar o próximo salto
        # (next_hop) a partir do endereço de destino do datagrama (dest_addr).
        # Retorne o next_hop para o dest_addr fornecido.

        tamanhoTabela=len(self.tabela)
        destinoLocalizado=False

        for i in range(0,tamanhoTabela):

            enderecoCIDR=self.tabela[i][1]
    
            qtdBitsFixos=self.tabela[i][0]

            next_hop=self.tabela[i][2]

            if self.verificaSaida(dest_addr, enderecoCIDR, qtdBitsFixos):
                return next_hop

        print('Utilizando rota padrao')
        return self.obtemRotaPadrao()

    def verificaSaida(self, enderecoIP, enderecoCIDR, qtdBitsFixos):


        print(' Verificando saida: enderecoIP: '+str(enderecoIP)+' enderecoCIDR: '+str(enderecoCIDR)+' qtdBitsFixos: '+str(qtdBitsFixos))

        posicaoIP=0

        while qtdBitsFixos>7:

            if int(enderecoCIDR.split('.')[posicaoIP]) != int(enderecoIP.split('.')[posicaoIP]):

                return False

            posicaoIP=posicaoIP+1

            qtdBitsFixos=qtdBitsFixos-8

        if qtdBitsFixos>0:

            bitsShift=8-qtdBitsFixos

            if int(enderecoCIDR.split('.')[posicaoIP])>>bitsShift != int(enderecoIP.split('.')[posicaoIP])>>bitsShift:

                return False

            else: 

                return True
        else:

            return True

    def obtemRotaPadrao(self):

        tamanhoTabela=len(self.tabela)

        for i in range(0,tamanhoTabela):

            enderecoCIDR=self.tabela[i][1]

            first_bitCIDR = int(enderecoCIDR.split('.')[0])>>7

            #verificando se o endereco destino eh igual a algum da tabela
            if int(enderecoCIDR.split('.')[0]) == 0 :
                
                return self.tabela[i][2]

        print('Rota padrao nao localizada')

    def definir_endereco_host(self, meu_endereco):
        """
        Define qual o endereço IPv4 (string no formato x.y.z.w) deste host.
        Se recebermos datagramas destinados a outros endereços em vez desse,
        atuaremos como roteador em vez de atuar como host.
        """
        self.meu_endereco = meu_endereco

    def definir_tabela_encaminhamento(self, tabela):
        """
        Define a tabela de encaminhamento no formato
        [(cidr0, next_hop0), (cidr1, next_hop1), ...]

        Onde os CIDR são fornecidos no formato 'x.y.z.w/n', e os
        next_hop são fornecidos no formato 'x.y.z.w'.
        """
        # TODO: Guarde a tabela de encaminhamento. Se julgar conveniente,
        # converta-a em uma estrutura de dados mais eficiente.

        '''
            A estrutura da tabela sera: [[nBitsFixos, IP base, rota],[...],[...],...]
        '''
        self.tabela = []

        tamanhoTabela=len(tabela)
        destinoLocalizado=False

        for i in range(0,tamanhoTabela):

            bitsFixos=int(tabela[i][0].split('/')[1])

            endereco=''

            self.tabela.append([bitsFixos,tabela[i][0].split('/')[0],tabela[i][1]])

        print(self.tabela)
        pass

    def registrar_recebedor(self, callback):
        """
        Registra uma função para ser chamada quando dados vierem da camada de rede
        """
        self.callback = callback

    def enviar(self, segmento, dest_addr):
        """
        Envia segmento para dest_addr, onde dest_addr é um endereço IPv4
        (string no formato x.y.z.w).
        """
        next_hop = self._next_hop(dest_addr)
        # TODO: Assumindo que a camada superior é o protocolo TCP, monte o
        # datagrama com o cabeçalho IP, contendo como payload o segmento.
        self.enlace.enviar(datagrama, next_hop)
