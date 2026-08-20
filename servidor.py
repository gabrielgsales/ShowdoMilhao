# servidor.py
# esse arquivo e o servidor do jogo Show do Milhao
# ele fica esperando o cliente se conectar e depois controla as rodadas

import socket
import random


# -- funcoes do RSA implementadas do zero --

# funcao para verificar se um numero e primo
# vai testando se alguem divide n ate a raiz quadrada
def e_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# funcao para calcular o maximo divisor comum usando o algoritmo de euclides
# serve para saber se dois numeros nao tem divisor em comum (mdc = 1)
def mdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a


# funcao para calcular o inverso modular usando o algoritmo de euclides estendido
# encontra o d tal que d * e mod phi = 1
def inverso_modular(e, phi):
    r_ant, r = e, phi
    s_ant, s = 1, 0
    while r != 0:
        q = r_ant // r
        r_ant, r = r, r_ant - q * r
        s_ant, s = s, s_ant - q * s
    if s_ant < 0:
        s_ant = s_ant + phi
    return s_ant


# funcao para gerar as chaves RSA usando p=61 e q=53
# retorna a chave publica como (e, n) e a chave privada como (d, n)
def gerar_chaves_rsa():
    p = 61
    q = 53

    # n e o modulo, vai ser igual a 3233
    n = p * q

    # phi e o totiente de euler, vai ser 3120
    phi = (p - 1) * (q - 1)

    # procura um e que seja coprimo com phi (mdc entre eles = 1)
    e = 2
    while e < phi:
        if mdc(e, phi) == 1:
            break
        e += 1

    # calcula o d que e o inverso modular de e em relacao ao phi
    d = inverso_modular(e, phi)

    return (e, n), (d, n)


# funcao para criptografar uma mensagem com RSA usando a chave publica do cliente
# cada letra vira um numero usando ord(), depois aplica pow(m, e, n)
# retorna uma lista de numeros inteiros separados por espaco
def criptografar_rsa(mensagem, e, n):
    cifrado = []
    for c in mensagem:
        m = ord(c)
        c_enc = pow(m, e, n)
        cifrado.append(c_enc)
    return cifrado


# funcao da cifra de cesar com deslocamento 3 em texto maiusculo
# letras avancam 3 posicoes no alfabeto, outros caracteres ficam igual
def cifra_cesar(texto, k=3):
    resultado = ""
    for c in texto.upper():
        if c.isalpha():
            nova = chr((ord(c) - ord('A') + k) % 26 + ord('A'))
            resultado += nova
        else:
            resultado += c
    return resultado


# -- banco de palavras para o jogo --

# cada lista interna tem 4 palavras e a certa e escolhida aleatoriamente a cada rodada
banco_de_palavras = [
    ["PALMEIRAS", "SANTOS", "GUARANI", "CORINTHIANS"],
    ["JUIZ", "GOLEIRO", "FLAMENGO", "NEYMAR"],
    ["PELE", "MESSI", "BRASIL", "ARGENTINA"],
    ["FUTEBOL", "ALEMANHA", "COPA", "MARACANA"],
    ["PEIXE", "GAVIAO", "RONALDO", "KAKA"],
    ["PAQUETA", "COMEMORACAO", "NARRADOR", "INTERVALO"],
    ["CAMPEAO", "LIBERTADORES", "BARCELONA", "VILA BELMIRO"],
    ["MORUMBI", "NEO QUIMICA", "MUNDIAL", "MINEIRO"],
]


def main():
    print("=== SERVIDOR - SHOW DO MILHAO ===")
    print()

    # gera as chaves RSA do servidor (nao sao usadas nesse jogo, so para fins didaticos)
    chave_publica_srv, chave_privada_srv = gerar_chaves_rsa()
    e_srv, n_srv = chave_publica_srv
    d_srv, _ = chave_privada_srv
    print(f"[RSA] Chaves do servidor geradas para fins didaticos.")
    print(f"      Chave publica: e={e_srv}, n={n_srv}")
    print(f"      Chave privada: d={d_srv} (mantida em segredo)")
    print()

    # cria o socket TCP e fica esperando o cliente conectar
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # essa opcao evita erro de porta ja em uso ao reiniciar o programa rapido
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor_socket.bind(('127.0.0.1', 65432))
    servidor_socket.listen(1)
    print("Aguardando o cliente se conectar na porta 65432...")

    conn, addr = servidor_socket.accept()
    print(f"Cliente conectado! Endereco: {addr}")
    print()

    # recebe a chave publica do cliente no formato CHAVE_PUB:e:n
    # o servidor vai usar essa chave para criptografar as dicas
    dados_chave = conn.recv(4096).decode('utf-8')
    partes_chave = dados_chave.split(":")
    e_cli = int(partes_chave[1])
    n_cli = int(partes_chave[2])
    print(f"[RSA] Chave publica do cliente recebida: e={e_cli}, n={n_cli}")
    print(f"      As dicas serao criptografadas com essa chave antes de enviar.")
    print()

    total_rodadas = 5
    vitorias_servidor = 0

    # embaralha o banco para nao usar sempre os mesmos grupos nas primeiras rodadas
    grupos = banco_de_palavras.copy()
    random.shuffle(grupos)

    for rodada in range(1, total_rodadas + 1):
        print(f"============ RODADA {rodada} DE {total_rodadas} ============")

        # pega as quatro palavras da rodada atual
        palavras = grupos[rodada - 1].copy()

        # escolhe aleatoriamente qual das quatro e a palavra certa nessa rodada
        palavra_certa = random.choice(palavras)

        # embaralha a ordem das palavras para o cliente nao perceber padrao
        random.shuffle(palavras)

        # descobre em qual posicao a palavra certa caiu depois de embaralhar
        posicao_certa = palavras.index(palavra_certa)

        # aplica a cifra de cesar em cada palavra para enviar cifrado ao cliente
        palavras_cifradas = [cifra_cesar(p) for p in palavras]

        # mostra para o jogador servidor as palavras ORIGINAIS (sem cifra)
        # e indica qual e a certa para ele poder dar a dica correta
        print()
        print("As palavras abaixo sao as originais (so voce ve isso aqui no servidor):")
        for i, p in enumerate(palavras):
            if i == posicao_certa:
                print(f"  {i + 1}. {p}  <--- ESSA E A PALAVRA CORRETA")
            else:
                print(f"  {i + 1}. {p}")
        print()

        # envia as palavras cifradas para o cliente no formato PALAVRAS:p1,p2,p3,p4
        msg_palavras = "PALAVRAS:" + ",".join(palavras_cifradas)
        conn.sendall(msg_palavras.encode('utf-8'))

        # pede para o jogador servidor digitar a dica
        dica = input("Digite uma dica para ajudar o cliente a descobrir a palavra certa: ").strip()

        # criptografa a dica caractere a caractere com a chave publica do cliente
        # assim so o cliente consegue ler, usando sua chave privada
        dica_cifrada = criptografar_rsa(dica, e_cli, n_cli)

        # envia a dica criptografada como numeros separados por espaco
        # formato: DICA:num1 num2 num3 ...
        msg_dica = "DICA:" + " ".join(str(x) for x in dica_cifrada)
        conn.sendall(msg_dica.encode('utf-8'))
        print(f"[RSA] Dica enviada criptografada com a chave publica do cliente.")

        # aguarda a resposta do cliente no formato ESCOLHA:numero
        dados_recebidos = conn.recv(4096).decode('utf-8')
        partes = dados_recebidos.split(":")
        numero_escolhido = int(partes[1])

        # verifica se o cliente escolheu a posicao certa
        # a posicao interna vai de 0 a 3 mas o cliente ve de 1 a 4
        if numero_escolhido - 1 == posicao_certa:
            resultado = "RESULTADO:VITORIA"
            vitorias_servidor += 1
            print(f"O cliente escolheu a opcao {numero_escolhido} e ACERTOU! A palavra era: {palavra_certa}")
        else:
            resultado = "RESULTADO:DERROTA"
            palavra_errada = palavras[numero_escolhido - 1]
            print(f"O cliente escolheu a opcao {numero_escolhido} ({palavra_errada}) e ERROU. A certa era: {palavra_certa}")

        # envia o resultado para o cliente
        conn.sendall(resultado.encode('utf-8'))
        print()

    # mostra o placar final do servidor
    print("=========================================")
    print(f"FIM DE JOGO! Resultado: {vitorias_servidor} vitoria(s) em {total_rodadas} rodadas.")
    if vitorias_servidor == total_rodadas:
        print("Voces acertaram tudo! Dupla perfeita!")
    elif vitorias_servidor >= total_rodadas // 2:
        print("Boa dupla! Mais da metade certa.")
    else:
        print("Precisa melhorar as dicas! Tente de novo.")
    print("=========================================")

    conn.close()
    servidor_socket.close()


main()
