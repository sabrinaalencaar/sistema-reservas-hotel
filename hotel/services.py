"""
Implementa as regras de negócio e operações principais do Sistema de Reservas de Hotel.
"""

from .models import Pessoa, Hospede, Quarto, QuartoLuxo, Pagamento, Adicional, Reserva
from hotel.data import salvar_dados, carregar_dados
from hotel import config
from datetime import datetime, date, timedelta
from typing import List, Optional
from .config import Cores
from time import sleep


# PERSISTÊNCIA TEMPORÁRIA EM MEMÓRIA: 

quartos_db: List[Quarto] = []
hospedes_db: List[Hospede] = []
reservas_db: List[Reserva] = []


# FUNCÕES DE BUSCA:

def buscar_quarto(numero: int) -> Optional[Quarto]:
    """
    Busca um quarto na lista pelo número.
    """
    for q in quartos_db:
        if q.numero == numero:
            return q
    return None

def buscar_hospede(documento: str) -> Optional[Hospede]:
    """
    Busca um hóspede na lista pelo documento.
    """
    for h in hospedes_db:
        if h.documento == documento:
            return h
    return None


# FUNÇÕES DE CADASTRO (CRUD):

def cadastrar_quarto(numero: int, tipo: str, capacidade: int, tarifa_base: float) -> Quarto:
    """
    Verifica se o quarto já existe e o cadastra se não existir.
    """
    if buscar_quarto(numero):
        raise ValueError(f"{Cores.VERMELHO}Erro: Já existe um quarto cadastrado com o número {numero}.{Cores.RESET}")
    
    novo_quarto = Quarto(numero, tipo, capacidade, tarifa_base)
    
    quartos_db.append(novo_quarto)
    return novo_quarto

def cadastrar_hospede(nome: str, documento: str, email: str, telefone: str) -> Hospede:
    """
    Verifica se o hóspede já existe e o cadastra se não existir.
    """
    if buscar_hospede(documento):
        raise ValueError(f"{Cores.VERMELHO}Erro: Hóspede com documento {documento} já está cadastrado.{Cores.RESET}")
        
    novo_hospede = Hospede(nome, documento, email, telefone)
    hospedes_db.append(novo_hospede)
    return novo_hospede


# GESTÃO DE RESERVAS:

def _verificar_disponibilidade(numero_quarto: int, data_inicio: date, data_fim: date) -> bool:
    """
    Verifica se o quarto está livre no período solicitado.
    """
    for r in reservas_db:
        if r.quarto.numero == numero_quarto and r.status != "CANCELADA":
            if data_inicio < r.data_saida and data_fim > r.data_entrada:
                return False
    return True

def realizar_reserva(doc_hospede: str, num_quarto: int, data_entrada: date, data_saida: date, num_hospedes: int) -> Reserva:
    """
    Tenta criar uma reserva vinculando um hóspede e um quarto.
    """
    hospede = buscar_hospede(doc_hospede)
    quarto = buscar_quarto(num_quarto)
    
    if not hospede:
        raise ValueError(f"{Cores.VERMELHO}Erro: Hóspede não encontrado. Cadastre-o antes.{Cores.RESET}")
    if not quarto:
        raise ValueError(f"{Cores.VERMELHO}Erro: Quarto não encontrado.{Cores.RESET}")

    if not _verificar_disponibilidade(num_quarto, data_entrada, data_saida):
        raise ValueError(f"{Cores.VERMELHO}O Quarto {num_quarto} já está ocupado neste período!{Cores.RESET}")

    if num_hospedes > quarto.capacidade:
        raise ValueError(f"{Cores.VERMELHO}Capacidade excedida. O quarto comporta {quarto.capacidade} pessoas.{Cores.RESET}")
    
    nova_reserva = Reserva(hospede, quarto, data_entrada, data_saida, num_hospedes)
    
    reservas_db.append(nova_reserva)
    hospede.historico_reservas.append(nova_reserva)
    
    return nova_reserva

def confirmar_reserva(doc_hospede: str, num_quarto: int):
    """
    Busca uma reserva PENDENTE e muda para CONFIRMADA.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada.{Cores.RESET}")

    if reserva.status != "PENDENTE":
        raise ValueError(f"{Cores.VERMELHO}Apenas reservas PENDENTES podem ser confirmadas. Status atual: {reserva.status}{Cores.RESET}")

    if reserva.confirmar():
        salvar_tudo()
        print(f"{Cores.VERDE}Reserva confirmada com sucesso para {reserva.hospede.nome}!{Cores.RESET}")
    else:
        raise ValueError(f"{Cores.VERMELHO}Não foi possível confirmar a reserva.{Cores.RESET}")

def cancelar_reserva(doc_hospede: str, num_quarto: int):
    """
    Cancela uma reserva e aplica multa se estiver fora do prazo.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada.{Cores.RESET}")
    
    if reserva.status not in ["PENDENTE", "CONFIRMADA"]:
        raise ValueError(f"{Cores.VERMELHO}Não é possível cancelar reserva com status {reserva.status}.{Cores.RESET}")

    politica = config.get_politica_cancelamento()
    horas_limite = politica.get("horas_limite_sem_multa", 24)
    multa_pct = politica.get("multa_padrao", 0.0)

    agora = datetime.now()
    data_checkin = datetime.combine(reserva.data_entrada, datetime.min.time()) 
    data_checkin = data_checkin.replace(hour=14)

    diferenca = data_checkin - agora
    horas_antecedencia = diferenca.total_seconds() / 3600

    print(f"Antecedência do cancelamento: {horas_antecedencia:.1f} horas.")

    if horas_antecedencia < horas_limite:
        valor_total = calcular_total_reserva(reserva)
        valor_multa = valor_total * multa_pct
        
        multa_obj = Adicional(f"Multa Cancelamento (<{horas_limite}h)", valor_multa)
        reserva.adicionais.append(multa_obj)
        
        print(f"Multa aplicada: R$ {valor_multa:.2f} ({multa_pct*100}% do total).")
    else:
        print("Cancelamento dentro do prazo. Sem multa.")

    reserva.cancelar()
    print(f"{Cores.VERDE}Reserva cancelada com sucesso e quarto liberado.{Cores.RESET}")

def realizar_noshow(doc_hospede: str, num_quarto: int):
    """
    Registra o não-comparecimento, aplica multa total e cancela a reserva.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada.{Cores.RESET}")
    
    if reserva.status != "CONFIRMADA":
        raise ValueError(f"{Cores.VERMELHO}Apenas reservas CONFIRMADAS podem sofrer No-Show. Status atual: {reserva.status}.{Cores.RESET}")

    horarios = config.get_horarios()
    tolerancia_min = horarios.get("tolerancia_noshow_minutos", 60)
    
    data_limite = datetime.combine(reserva.data_entrada, datetime.min.time())
    data_limite = data_limite.replace(hour=14) + timedelta(minutes=tolerancia_min)
    
    agora = datetime.now()
    
    if agora < data_limite:
        print(f"Atenção: Ainda está dentro do prazo de tolerância (Limite: {data_limite}).")
        confirmacao = input("Deseja registrar o No-Show mesmo assim? (S/N): ")
        if confirmacao.upper() != 'S':
            return

    multa_pct = config.get_multa_noshow()
    valor_total = calcular_total_reserva(reserva)
    valor_multa = valor_total * multa_pct
    
    reserva.adicionais.append(Adicional("Multa NO-SHOW", valor_multa))
    reserva.status = "NO_SHOW"
    reserva.quarto.liberar_quarto()
    
    print(f"No-Show registrado para {reserva.hospede.nome}.")
    print(f"Multa aplicada: R$ {valor_multa:.2f}")


# CÁLCULO DE VALORES E TARIFAS:

def calcular_total_reserva(reserva: Reserva) -> float:
    """
    Calcula o valor final da reserva percorrendo dia a dia e aplicando
    as regras de temporada e fim de semana.
    Soma também os adicionais e aplica a taxa de serviço.
    """
    total_diarias = 0.0
    dia_atual = reserva.data_entrada
    
    # LOOP: Percorre do dia da entrada até o dia da saída
    while dia_atual < reserva.data_saida:
        # Usa a função que já criamos para saber o preço daquele dia específico
        valor_do_dia = calcular_valor_diaria(dia_atual, reserva.quarto.tarifa_base)
        total_diarias += valor_do_dia
        
        # Avança para o próximo dia
        dia_atual += timedelta(days=1)
    
    # Soma os consumos extras
    total_adicionais = sum(item.valor for item in reserva.adicionais)
    
    subtotal = total_diarias + total_adicionais
    
    # Aplica Taxa de Serviço (ex: 10%) definida no settings.json
    taxa_servico_pct = config.get_taxa_servico() # ex: 0.10
    valor_taxa = subtotal * taxa_servico_pct
    
    total_final = subtotal + valor_taxa
    
    return total_final


# FLUXO DA ESTADIA (CHECK-IN / CHECK-OUT):

def buscar_reserva(hospede_doc: str, quarto_num: int) -> Optional[Reserva]:
    """
    Busca uma reserva ativa pelo documento do hóspede e número do quarto.
    """
    for r in reservas_db:
        if r.hospede.documento == hospede_doc and r.quarto.numero == quarto_num:
            return r
    return None

def realizar_checkin(doc_hospede: str, num_quarto: int):
    """
    Busca a reserva e tenta fazer o check-in, atualizando o status do quarto.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada para este hóspede/quarto.{Cores.RESET}")
    
    if reserva.checkin():
        quarto_real = buscar_quarto(num_quarto)
        if quarto_real:
            quarto_real.status = "OCUPADO"
        
        salvar_tudo()
    else:
        raise ValueError(f"{Cores.VERMELHO}Não foi possível realizar o check-in (Verifique se a reserva está CONFIRMADA).{Cores.RESET}")

def realizar_checkout(doc_hospede: str, num_quarto: int):
    """
    Busca a reserva, calcula total, verifica pagamento e libera o quarto.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada para este hóspede/quarto.{Cores.RESET}")
    
    total_conta = calcular_total_reserva(reserva)
    total_pago = sum(p.valor for p in reserva.pagamentos)
    
    print(f"\n--- FECHAMENTO DE CONTA ---")
    print(f"Total da Hospedagem: R$ {total_conta:.2f}")
    print(f"Total Pago:          R$ {total_pago:.2f}")
    
    if total_pago < (total_conta - 0.01):
        faltando = total_conta - total_pago
        raise ValueError(f"{Cores.VERMELHO}Conta pendente! Faltam R$ {faltando:.2f} para liberar a saída.{Cores.RESET}")
    
    if reserva.checkout():
        quarto_real = buscar_quarto(num_quarto)
        if quarto_real:
            quarto_real.status = "DISPONIVEL"
            
        salvar_tudo()
        
        print(f"{Cores.VERDE}Check-out realizado com sucesso! Quarto {num_quarto} liberado.{Cores.RESET}")
    else:
        raise ValueError(f"{Cores.VERMELHO}Não foi possível realizar o check-out.{Cores.RESET}")


# TRANSAÇÕES FINANCEIRAS:

def registrar_pagamento(doc_hospede: str, num_quarto: int, valor: float, forma: str):
    """
    Registra um pagamento para a reserva especificada e salva no banco.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada.{Cores.RESET}")
        
    pagamento = Pagamento(valor, forma)
    reserva.pagamentos.append(pagamento)
    
    salvar_tudo() 

def registrar_adicional(doc_hospede: str, num_quarto: int, descricao: str, valor: float):
    """
    Lança um consumo extra e salva no banco.
    """
    reserva = buscar_reserva(doc_hospede, num_quarto)
    if not reserva:
        raise ValueError(f"{Cores.VERMELHO}Reserva não encontrada para este hóspede/quarto.{Cores.RESET}")

    adicional = Adicional(descricao, valor)
    reserva.adicionais.append(adicional)
    
    salvar_tudo()


# PERSISTÊNCIA DE DADOS:

def inicializar_sistema():
    """
    Carrega os dados salvos ao iniciar o sistema.
    """
    global quartos_db, hospedes_db, reservas_db
    quartos_db, hospedes_db, reservas_db = carregar_dados()

    # Dados de Seed:
    if len(quartos_db) == 0:
        print(f"{Cores.AMARELO}Sistema vazio detectado. Criando dados de exemplo para teste...{Cores.RESET}")
        sleep(3)
        
        q1 = Quarto(101, "SIMPLES", 1, 100.0)
        q2 = Quarto(201, "DUPLO", 2, 150.0)
        q3 = Quarto(401, "LUXO", 2, 300.0)
        
        quartos_db.extend([q1, q2, q3])
        
        h1 = Hospede("Jayr Alencar", "000.000.000-00", "jayr@ufca.edu.br", "(88) 99999-9999")
        hospedes_db.append(h1)
        
        salvar_tudo()
            
        print(f"{Cores.VERDE}Dados de Seed (Quartos e Hóspedes) criados com sucesso!{Cores.RESET}")

def salvar_tudo():
    """
    Salva o estado atual das listas nos arquivos JSON.
    """
    salvar_dados(quartos_db, hospedes_db, reservas_db)


# RELATÓRIOS E ESTATÍSTICAS:

def gerar_relatorio_ocupacao():
    """
    Gera um relatório simples da taxa de ocupação atual do hotel.
    """
    total_quartos = len(quartos_db)
    
    if total_quartos == 0:
        print("Relatório indisponível: Nenhum quarto cadastrado.")
        return

    quartos_ocupados = 0
    for quarto in quartos_db:
        if quarto.status == "OCUPADO":
            quartos_ocupados += 1
            
    taxa = (quartos_ocupados / total_quartos) * 100
    
    print("\n" + "="*30)
    print(f"RELATÓRIO DE OCUPAÇÃO")
    print("="*30)
    print(f"Total de Quartos:   {total_quartos}")
    print(f"Quartos Ocupados:   {quartos_ocupados}")
    print(f"Quartos Livres:     {total_quartos - quartos_ocupados}")
    print("-" * 30)
    print(f"Taxa de Ocupação:   {taxa:.2f}%")
    print("="*30 + "\n")
    
    return taxa

def gerar_relatorio_financeiro():
    """
    - ADR (Diária Média): Quanto pagam em média por quarto.
    - RevPAR: Receita dividida pelo total de quartos (sucesso financeiro).
    - Taxa de Cancelamento.
    """
    total_quartos = len(quartos_db)
    if total_quartos == 0:
        print("Nenhum quarto cadastrado. Impossível calcular métricas.")
        return

    reservas_validas = [r for r in reservas_db if r.status in ["CONFIRMADA", "CHECKIN", "CHECKOUT"]]
    reservas_canceladas = [r for r in reservas_db if r.status == "CANCELADA"]
    
    total_receita = sum(calcular_total_reserva(r) for r in reservas_validas)
    quartos_vendidos = len(reservas_validas)
    total_reservas = len(reservas_db)
    
    # ADR (Average Daily Rate):
    adr = total_receita / quartos_vendidos if quartos_vendidos > 0 else 0.0
    
    # RevPAR (Revenue Per Available Room):
    revpar = total_receita / total_quartos
    
    # Taxa de Cancelamento:
    taxa_cancelamento = (len(reservas_canceladas) / total_reservas * 100) if total_reservas > 0 else 0.0

    print("\n" + "="*40)
    print(f"RELATÓRIO FINANCEIRO DO HOTEL")
    print("="*40)
    print(f"Receita Bruta Total:    R$ {total_receita:.2f}")
    print("-" * 40)
    print(f"Métricas Financeiras:")
    print(f"   • ADR (Diária Média):   R$ {adr:.2f}")
    print(f"   • RevPAR (Eficiência):  R$ {revpar:.2f}")
    print("-" * 40)
    print(f"Estatísticas:")
    print(f"   • Reservas Totais:      {total_reservas}")
    print(f"   • Cancelamentos:        {len(reservas_canceladas)} ({taxa_cancelamento:.1f}%)")
    print("="*40 + "\n")

    return {
        "receita": total_receita,
        "adr": adr,
        "revpar": revpar,
        "cancelamento": taxa_cancelamento
    }

# CÁLCULO DE TARIFAS

def _verificar_temporada(data: date) -> float:
    """
    Verifica se a data cai em alguma temporada e retorna o multiplicador.
    """
    temporadas = config.get_temporadas()
    
    for temp in temporadas:
        inicio_str = temp["inicio"]
        fim_str = temp["fim"]
        
        ano_atual = data.year
        
        d_inicio = datetime.strptime(f"{inicio_str}-{ano_atual}", "%d-%m-%Y").date()
        d_fim = datetime.strptime(f"{fim_str}-{ano_atual}", "%d-%m-%Y").date()
        
        if d_inicio > d_fim:  # Temporada que cruza o ano novo
            if data < d_inicio: 
                d_inicio = d_inicio.replace(year=ano_atual - 1)
            else:
                d_fim = d_fim.replace(year=ano_atual + 1)

        if d_inicio <= data <= d_fim:
            return temp["multiplicador"]
            
    return 1.0 # Tarifa normal

def calcular_valor_diaria(data: date, tarifa_base: float) -> float:
    """
    Calcula o preço de UMA diária específica aplicando as regras.
    """
    mult_temp = _verificar_temporada(data)
    mult_fds = 1.0
    
    if data.weekday() >= 5:
        mult_fds = config.get_multiplicador_fim_de_semana()
        
    valor_final = tarifa_base * mult_temp * mult_fds
    return valor_final