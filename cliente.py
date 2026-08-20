# cliente.py
# esse arquivo e o cliente do jogo Show do Milhao
# ele se conecta ao servidor e participa das rodadas tentando adivinhar a palavra certa

import socket


# -- funcoes do RSA implementadas do zero --

# funcao para verificar se um numero e primo
# vai testando divisores ate a raiz quadrada do numero
def e_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


# funcao para calcular o maximo divisor comum pelo algoritmo de euclides
def mdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a


# funcao do algoritmo de euclides estendido para achar o inverso modular
# retorna o d tal que d * e mod phi = 1
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


# funcao para gerar as chaves RSA com p=61 e q=53
# retorna a chave publica (e, n) e a chave privada (d, n)
def gerar_chaves_rsa():
    p = 61
    q = 53

    # n e o modulo, fica igual a 3233
    n = p * q

    # phi e o totiente de euler, fica igual a 3120
    phi = (p - 1) * (q - 1)

    # procura um e que seja coprimo com phi
    e = 2
    while e < phi:
        if mdc(e, phi) == 1:
            break
        e += 1

    # calcula d pelo inverso modular de e em relacao ao phi
    d = inverso_modular(e, phi)

    return (e, n), (d, n)


# funcao para descriptografar uma lista de numeros com RSA
# cada numero vira uma letra usando pow(c, d, n) e depois chr()
def descriptografar_rsa(cifrado, d, n):
    mensagem = ""
    for c in cifrado:
        m = pow(c, d, n)
        mensagem += chr(m)
    return mensagem


# funcao de ajuda para mostrar como funciona a cifra de cesar
# mostra uma tabelinha simples para o jogador entender como descriptografar
def mostrar_instrucao_cesar():
    print("-------------------------------------------------------")
    print("COMO DESCRIPTOGRAFAR AS PALAVRAS (Cifra de Cesar):")
    print("  Cada letra foi avancada 3 posicoes no alfabeto.")
    print("  Para desfazer, volte 3 posicoes em cada letra.")
    print()
    print("  Exemplos rapidos:")
    print("    D -> A    E -> B    F -> C    G -> D")
    print("    H -> E    I -> F    J -> G    K -> H")
    print("    L -> I    M -> J    N -> K    O -> L")
    print("    P -> M    Q -> N    R -> O    S -> P")
    print("    T -> Q    U -> R    V -> S    W -> T")
    print("    X -> U    Y -> V    Z -> W")
    print()
    print("  Se travar nas primeiras letras (A, B, C):")
    print("    A -> X    B -> Y    C -> Z")
    print("-------------------------------------------------------")


def main():
    print("=== CLIENTE - SHOW DO MILHAO ===")
    print()

    # gera as chaves RSA do cliente
    # a chave publica sera enviada ao servidor para ele criptografar as dicas
    # a chave privada fica so com o cliente para descriptografar as dicas recebidas
    chave_publica, chave_privada = gerar_chaves_rsa()
    e_cli, n_cli = chave_publica
    d_cli, _ = chave_privada

    print(f"[RSA] Chaves do cliente geradas.")
    print(f"      Chave publica: e={e_cli}, n={n_cli}  (sera enviada ao servidor)")
    print(f"      Chave privada: d={d_cli}  (fica guardada so com voce)")
    print()

    # cria o socket TCP e conecta no servidor
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_socket.connect(('127.0.0.1', 65432))
    print("Conectado ao servidor com sucesso!")
    print()

    # envia a chave publica para o servidor no formato CHAVE_PUB:e:n
    # o servidor usara essa chave para criptografar as dicas antes de enviar
    msg_chave = f"CHAVE_PUB:{e_cli}:{n_cli}"
    cliente_socket.sendall(msg_chave.encode('utf-8'))
    print(f"[RSA] Chave publica enviada ao servidor.")
    print(f"      A partir de agora as dicas chegam criptografadas e so voce pode ler.")
    print()

    total_rodadas = 5
    vitorias_cliente = 0

    for rodada in range(1, total_rodadas + 1):
        print(f"============ RODADA {rodada} DE {total_rodadas} ============")
        print()

        # recebe as palavras cifradas no formato PALAVRAS:p1,p2,p3,p4
        dados_palavras = cliente_socket.recv(4096).decode('utf-8')
        palavras_cifradas = dados_palavras.split(":")[1].split(",")

        # recebe a dica criptografada com RSA no formato DICA:num1 num2 num3 ...
        dados_dica = cliente_socket.recv(4096).decode('utf-8')
        numeros_dica = dados_dica.split(":", 1)[1]

        # converte os numeros recebidos de volta para inteiros
        lista_numeros = [int(x) for x in numeros_dica.split()]

        # mostra os numeros cifrados recebidos
        print(f"Dica cifrada recebida (numeros RSA): {lista_numeros}")
        print()
        print(f"Sua chave privada e: d={d_cli}, n={n_cli}")
        d_digitado = int(input("Digite sua chave privada (d) para descriptografar a dica: "))
        n_digitado = int(input("Digite o modulo (n): "))

        # descriptografa usando o que o usuario digitou
        dica_decifrada = descriptografar_rsa(lista_numeros, d_digitado, n_digitado)
        print(f"Dica descriptografada: {dica_decifrada}")
        print()

        # mostra a instrucao de como descriptografar as palavras
        mostrar_instrucao_cesar()
        print()



        # mostra as palavras cifradas numeradas para o jogador escolher
        print("Palavras cifradas (use a tabela acima para descobrir cada uma):")
        for i, p in enumerate(palavras_cifradas):
            print(f"  {i + 1}. {p}")
        print()

        # pede para o jogador cliente escolher uma das palavras
        while True:
            try:
                escolha = int(input("Qual e a palavra certa? Digite o numero de 1 a 4: "))
                if 1 <= escolha <= 4:
                    break
                else:
                    print("Digite um numero entre 1 e 4.")
            except ValueError:
                print("Isso nao e um numero. Tente de novo.")

        # envia a escolha para o servidor no formato ESCOLHA:numero
        msg_escolha = f"ESCOLHA:{escolha}"
        cliente_socket.sendall(msg_escolha.encode('utf-8'))

        # recebe o resultado da rodada
        dados_resultado = cliente_socket.recv(4096).decode('utf-8')
        resultado = dados_resultado.split(":")[1]

        if resultado == "VITORIA":
            vitorias_cliente += 1
            print()
            print("*** VITORIA! Voce acertou a palavra certa! ***")
        else:
            print()
            print("--- DERROTA. Nao foi dessa vez. ---")

        print()

    # mostra o placar final do cliente
    print("=========================================")
    print(f"FIM DE JOGO! Voce acertou {vitorias_cliente} de {total_rodadas} rodadas.")
    if vitorias_cliente == total_rodadas:
        print("Incrivel! Acertou tudo!")
    elif vitorias_cliente >= total_rodadas // 2:
        print("Bom trabalho! Mais da metade certa.")
    else:
        print("Ainda da para melhorar, tenta de novo!")
    print("=========================================")

    cliente_socket.close()


main()
