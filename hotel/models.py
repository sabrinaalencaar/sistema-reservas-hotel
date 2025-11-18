"""
Armazena as definições de classe para o Sistema de Reservas de Hotel.
"""

from datetime import date, datetime
from typing import List

class Pessoa:
    """
    Classe base para representar uma pessoa com dados cadastrais.
    
    Atributos:
        nome (str): Nome completo.
        documento (str): CPF ou Passaporte (único).
        email (str): E-mail de contato.
        telefone (str): Telefone de contato.
    """
    pass


class Hospede(Pessoa):
    """
    Representa um hóspede do hotel, herdando de Pessoa e contendo histórico de reservas.

    Atributos:
        historico_reservas (List[Reserva]): Lista de reservas associadas a este hóspede.
    """
    pass


class Quarto:
    """
    Classe base que representa um quarto e define seus atributos e regras principais.

    Atributos:
        numero (int): Número único do quarto.
        tipo (str): Categoria (SIMPLES, DUPLO, LUXO).
        capacidade (int): Número máximo de hóspedes.
        tarifa_base (float): Custo padrão da diária.
        status (str): Situação atual (DISPONIVEL, OCUPADO, MANUTENCAO).
    """

    def bloquear_quarto(self, data_inicio: date, data_fim: date, motivo: str):
        """
        Altera o status do quarto para MANUTENCAO por um período determinado.
        """
        pass

    def liberar_quarto(self):
        """
        Define o status do quarto como DISPONIVEL.
        """
        pass

    def __str__(self) -> str:
        """
        Retorna um resumo textual do quarto (ex: "Quarto 101 (LUXO)").
        """
        return f"Quarto {self.numero} ({self.tipo})" # Exemplo
        pass
    
    def __lt__(self, other: 'Quarto') -> bool:
        """
        Permite a ordenação de quartos, por tipo ou numeração.
        """
        pass


class QuartoLuxo(Quarto):
    """
    Subclasse de Quarto, representando um quarto tipo LUXO.
    Pode sobrescrever regras de tarifa.
    """
    pass


class Pagamento:
    """
    Representa um pagamento (parcial ou total) associado a uma Reserva.

    Atributos :
        data (datetime): Data e hora do pagamento.
        forma (str): Forma de pagamento (dinheiro, crédito, PIX).
        valor (float): Quantia paga.
    """
    pass


class Adicional:
    """
    Representa um consumo extra (ex.: frigobar, estacionamento) lançado na Reserva.

    Atributos :
        descricao (str): Descrição do item.
        valor (float): Custo do item.
    """
    pass


class Reserva:
    """
    Classe que gerencia as informações de reserva, conectando um Hóspede, um Quarto e um período de tempo.

    Atributos :
        hospede (Hospede): O hóspede responsável pela reserva.
        quarto (Quarto): O quarto reservado.
        data_entrada (date): Data de início da reserva.
        data_saida (date): Data de término da reserva.
        num_hospedes (int): Quantidade de pessoas no quarto.
        status (str): Situação da reserva (PENDENTE, CONFIRMADA, CHECKIN, CHECKOUT, CANCELADA, NO_SHOW).
        pagamentos (List[Pagamento]): Lista de pagamentos feitos.
        adicionais (List[Adicional]): Lista de consumos adicionais.
    """
    
    def confirmar(self):
        """
        Muda o status da reserva para CONFIRMADA.
        """
        pass

    def fazer_checkin(self):
        """
        Verifica se a data está correta e muda o status para CHECKIN.
        """
        pass

    def fazer_checkout(self):
        """
        Realiza o fechamento da conta e muda o status para CHECKOUT.
        """
        pass

    def cancelar(self):
        """
        Cancela a reserva e verifica regras de multa.
        """
        pass

    def calcular_total(self) -> float:
        """
        Calcula o valor total da reserva com base nas diárias, ajustes de temporada e adicionais.
        """
        pass

    def __len__(self) -> int:
        """
        Retorna o número de diárias (noites) da reserva.
        """
        pass

    def __eq__(self, other: 'Reserva') -> bool:
        """
        Verifica se duas reservas são idênticas (mesmo quarto e intervalo de datas que se sobrepõem).
        """
        pass