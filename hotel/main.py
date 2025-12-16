"""
Interface de Linha de Comando (CLI) principal do sistema.
Permite ao usuário interagir com o sistema de gestão de hotel via terminal.
"""

from .models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from hotel import services, config
from datetime import datetime, date
from time import sleep
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
            print("Quarto cadastrado com sucesso!")
            
        elif opcao == "2":
            nome = input("Nome Completo: ")
            documento = input("CPF/Documento: ")
            email = input("E-mail: ")
            telefone = input("Telefone: ")
            services.cadastrar_hospede(nome, documento, email, telefone)
            print("Hóspede cadastrado com sucesso!")
            
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
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    try:
        if opcao == "1":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            data_entrada = ler_data("Data de Entrada")
            data_saida = ler_data("Data de Saída")
            capacidade = int(input("Qtd. Hóspedes: "))
            
            reserva = services.realizar_reserva(documento, numero, data_entrada, data_saida, capacidade)
            total_previsto = services.calcular_total_reserva(reserva)
            print(f"Reserva realizada com sucesso! Valor previsto: R$ {total_previsto:.2f}")
            
        elif opcao == "2":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            r = services.buscar_reserva(documento, numero)
            if r:
                print(f"\nReserva encontrada: {r.status}")
                print(f"Período: {r.data_entrada} até {r.data_saida}")
            else:
                print("Reserva não encontrada.")

        elif opcao == "3":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            print("Calculando multas...")
            services.cancelar_reserva(documento, numero)

    except Exception as e:
        print(f"Erro: {e}")
        
    if opcao != "0": pausar()

def menu_recepcao():
    exibir_cabecalho()
    print("RECEPÇÃO (CHECK-IN / OUT)")
    print("-" * 50)
    print("1. Realizar Check-in (Entrada)")
    print("2. Realizar Check-out (Saída e Pagamento)")
    print("3. Registrar No-Show (Não compareceu)")
    print("0. Voltar")
    print("-" * 50)
    
    opcao = input("Opção: ")
    
    try:
        if opcao == "1":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_checkin(documento, numero)
            print("Check-in realizado com sucesso! Bem-vindo.")
            
        elif opcao == "2":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_checkout(documento, numero)
            
        elif opcao == "3":
            documento = input("CPF do Hóspede: ")
            numero = int(input("Número do Quarto: "))
            services.realizar_noshow(documento, numero)

    except Exception as e:
        print(f"Erro: {e}")
        
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
        print("1. Cadastros (Quartos/Hóspedes)")
        print("2. Reservas")
        print("3. Recepção (Check-in/Check-out/No-Show)")
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
            services.salvar_tudo()
            print("Até logo!")
            break
        else:
            print("Opção inválida!")
            sleep(1)

if __name__ == "__main__":
    main()