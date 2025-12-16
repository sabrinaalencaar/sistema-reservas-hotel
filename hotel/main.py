"""
Interface de Linha de Comando (CLI) principal do sistema.
Permite ao usuário interagir com o sistema de gestão de hotel via terminal.
"""

from .models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from hotel import services, config
from datetime import datetime, date
from time import sleep
from .config import Cores
import sys
import os


def limpar_tela():
    """
    Limpa o terminal para ficar visualmente agradável.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    """
    Pausa para o usuário ler a mensagem.
    """
    input("\nPressione ENTER para continuar...")

def ler_data(mensagem: str) -> date:
    """
    Função para ler data sem quebrar o programa.
    """
    while True:
        entrada = input(f"{mensagem} (DD/MM/AAAA): ")
        try:
            return datetime.strptime(entrada, "%d/%m/%Y").date()
        except ValueError:
            print("Data inválida! Use o formato DD/MM/AAAA (ex: 25/12/2025).")

def exibir_cabecalho():
    limpar_tela()
    print("="*50)
    print(f"{config.get_info_hotel().get('nome', 'HOTEL SYSTEM').center(50)}")
    print("="*50)


# MENUS ESPECÍFICOS

def menu_cadastros():
    exibir_cabecalho()
    print("GESTÃO DE CADASTROS")
    print("-" * 50)
    print("1. Cadastrar Novo Quarto")
    print("2. Cadastrar Novo Hóspede")
    print("3. Listar Quartos")
    print("4. Listar Hóspedes")
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    try:
        if opcao == "1":
            numero = int(input("Número do Quarto: "))
            tipo = input("Tipo (SIMPLES/DUPLO/LUXO): ").upper()
            capacidade = int(input("Capacidade de pessoas: "))
            tarifa_base = float(input("Preço da Diária (R$): "))
            services.cadastrar_quarto(numero, tipo, capacidade, tarifa_base)
            print(f"{Cores.VERDE}Quarto cadastrado com sucesso!{Cores.RESET}")
            
        elif opcao == "2":
            nome = input("Nome Completo: ")
            documento = input("CPF/Documento: ")
            email = input("E-mail: ")
            telefone = input("Telefone: ")
            services.cadastrar_hospede(nome, documento, email, telefone)
            print(f"{Cores.VERDE}Hóspede cadastrado com sucesso!{Cores.RESET}")
            
        elif opcao == "3":
            print("\n--- LISTA DE QUARTOS ---")
            for q in services.quartos_db:
                print(f"Quarto {q.numero} | Tipo: {q.tipo} | Preço: R${q.tarifa_base:.2f} | Status: {q.status}")
                
        elif opcao == "4":
            print("\n--- LISTA DE HÓSPEDES ---")
            for h in services.hospedes_db:
                print(f"Nome: {h.nome} | Doc: {h.documento}")

    except Exception as e:
        print(f"Erro: {e}")
    
    if opcao != "0": pausar()

def menu_reservas():
    exibir_cabecalho()
    print("GESTÃO DE RESERVAS")
    print("-" * 50)
    print("1. Nova Reserva")
    print("2. Buscar Reserva")
    print("3. Cancelar Reserva (Com cálculo de multa)")
    print("4. Confirmar Reserva")
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    try:
        if opcao == "1":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            data_entrada = ler_data("Data de Entrada")
            data_saida = ler_data("Data de Saída")
            num_hospedes = int(input("Qtd. Hóspedes: "))
            
            reserva = services.realizar_reserva(documento, numero, data_entrada, data_saida, num_hospedes)
            total_previsto = services.calcular_total_reserva(reserva)
            print(f"{Cores.VERDE}Reserva realizada com sucesso!{Cores.RESET} Valor previsto: R$ {total_previsto:.2f}")
            
        elif opcao == "2":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            r = services.buscar_reserva(documento, numero)
            if r:
                print(f"\nReserva encontrada: {r.status}")
                print(f"Período: {r.data_entrada} até {r.data_saida}")
            else:
                print(f"{Cores.VERMELHO}Reserva não encontrada.{Cores.RESET}")

        elif opcao == "3":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            print("Calculando multas...")
            services.cancelar_reserva(documento, numero)

        elif opcao == "4":
            doc = input("CPF do Hóspede: ")
            num = int(input("Número do Quarto: "))
            services.confirmar_reserva(doc, num)
            pausar()

    except Exception as e:
        print(f"{Cores.VERMELHO}Erro: {e}{Cores.RESET}")
        
    if opcao != "0": pausar()

def menu_recepcao():
    exibir_cabecalho()
    print("RECEPÇÃO (CHECK-IN / OUT)")
    print("-" * 50)
    print("1. Realizar Check-in (Entrada)")
    print("2. Realizar Check-out (Saída e Pagamento)")
    print("3. Registrar No-Show (Não compareceu)")
    print("4. Registrar Pagamento (Adiantamento)")
    print("5. Lançar Consumo Extra (Frigobar/Serviços)")
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    try:
        if opcao == "1":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_checkin(documento, numero)
            print(f"{Cores.VERDE}Check-in realizado com sucesso! Bem-vindo!{Cores.RESET}")
            
        elif opcao == "2":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_checkout(documento, numero)
            
        elif opcao == "3":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_noshow(documento, numero)

        elif opcao == "4":
            print("\n--- NOVO PAGAMENTO ---")
            doc = input("CPF do Hóspede: ")
            num = int(input("Número do Quarto: "))
            valor = float(input("Valor (R$): "))
            print("""Forma: 
                  [1] Pix 
                  [2] Dinheiro 
                  [3] Cartão de Débito 
                  [4] Cartão de Crédito""")
            op_forma = input("Escolha: ")
            forma = "PIX" if op_forma == "1" else "DINHEIRO" if op_forma == "2" else "CARTAO_DEBITO" if op_forma == "3" else "CARTAO_CREDITO"
            
            services.registrar_pagamento(doc, num, valor, forma)
            print(f"{Cores.VERDE}Pagamento registrado com sucesso!{Cores.RESET}")

        elif opcao == "5":
            print("\n--- NOVO CONSUMO ---")
            doc = input("CPF do Hóspede: ")
            num = int(input("Número do Quarto: "))
            item = input("Descrição do item: ")
            valor = float(input("Valor (R$): "))
            
            services.registrar_adicional(doc, num, item, valor)
            print(f"{Cores.VERDE}Item adicionado à conta com sucesso!{Cores.RESET}")

    except Exception as e:
        print(f"{Cores.VERMELHO}Erro: {e}{Cores.RESET}")
        
    if opcao != "0": pausar()

def menu_relatorios():
    exibir_cabecalho()
    print("RELATÓRIOS")
    print("-" * 50)
    print("1. Ocupação Atual")
    print("2. Financeiro Completo (ADR/RevPAR)")
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    if opcao == "1":
        services.gerar_relatorio_ocupacao()
        pausar()
    elif opcao == "2":
        services.gerar_relatorio_financeiro()
        pausar()


# LOOP PRINCIPAL

def main():
    # Carrega configurações do JSON:
    config.carregar_configuracoes()
    
    # Carrega dados salvos:
    services.inicializar_sistema()
    
    while True:
        exibir_cabecalho()
        print("MENU PRINCIPAL")
        print("-" * 50)
        print("1. Cadastros")
        print("2. Reservas")
        print("3. Recepção")
        print("4. Relatórios")
        print("0. SAIR e SALVAR")
        print("-" * 50)
        
        opcao = input("Escolha uma opção: ")
        
        if opcao == "1":
            menu_cadastros()
        elif opcao == "2":
            menu_reservas()
        elif opcao == "3":
            menu_recepcao()
        elif opcao == "4":
            menu_relatorios()
        elif opcao == "0":
            print("\nSalvando dados...")
            sleep(3)
            services.salvar_tudo()
            print("Até logo!")
            break
        else:
            print(f"{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
            sleep(1)

if __name__ == "__main__":
    main()