# Sistema de Reservas de Hotel

Projeto para a disciplina de Programação Orientada a Objetos (POO) da Universidade Federal do Cariri (UFCA).

## Descrição e Objetivo

Este é o sistema de gerenciamento de reservas para um hotel, desenvolvido em **Python** e estruturado com princípios de POO, como **herança**, **encapsulamento** e **composição**. A aplicação consiste em uma **interface de linha de comando (CLI)**, projetada para simular o fluxo operacional completo de um hotel, desde a entrada do hóspede até o fechamento da conta.

Além de gerenciar o fluxo de reservas, o sistema implementa regras de negócio essenciais:
* **Cálculo de Tarifas:** Aplicação de multiplicadores de preço por temporada e fim de semana.
* **Controle de Transições:** Gerenciamento dos estados da reserva (PENDENTE a CHECKOUT, incluindo regras de NO\_SHOW e Cancelamento com multa).
* **Relatórios:** Geração de métricas gerenciais importantes, como Taxa de Ocupação, ADR e RevPAR.
* **Persistência de Dados:** Uso de JSON para salvar e carregar todas as informações do sistema.

## Estrutura de Arquivos

```
hotel-manager/
├── hotel/
│   ├── __init__.py
│   ├── data.py
│   ├── main.py
│   ├── models.py
│   └── services.py
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
│
├── .gitignore
├── LICENSE
├── README.md
└── settings.json
```

## Estrutura Planejada de Classes (UML Textual)

A modelagem inicial do sistema segue a estrutura abaixo.

### Classes Principais

* Classe `Pessoa`
    * **Atributos**: nome, documento, email, telefone
* Classe `Hospede` (Herda de Pessoa)
    * **Atributos**: historico_reservas
* Classe `Quarto`
    * **Atributos**: numero, tipo, capacidade, tarifa_base, status
    * **Métodos**: bloquear_quarto(), liberar_quarto(), str(), lt()
    * **Subclasse**: `QuartoLuxo`
* Classe `Reserva`
    * **Atributos**: hospede; quarto; data_entrada; data_saida; num_hospedes; status; pagamentos; adicionais;
    * **Métodos**: confirmar(), checkin(), checkout(), cancelar(),
calcular_total(), len(), eq()
* Classe `Pagamento`
    * **Atributos**: data, forma, valor
* Classe `Adicional`
    * **Atributos**: descricao, valor

### Relacionamentos

* **Herança**:
    * `Hospede` herda de `Pessoa`.
    * `QuartoLuxo` herda de `Quarto`.

* **Agregação**: 
    * `Reserva` agrega `Pagamentos` e `Adicionais`.

* **Associação**:
    * `Reserva` está ligada a um `Hospede` e a um `Quarto`.
    * `Hospede` pode ter várias `Reservas`.