# Widget de Cross-sell no Conexa

## O que é Cross-sell?

**Definição e Importância**

Cross-sell é uma estratégia de vendas que envolve oferecer produtos ou serviços complementares aos que os clientes já compraram. Para empresas que oferecem serviços recorrentes, o Cross-sell é uma ferramenta essencial para maximizar o valor de cada cliente, oferecendo soluções complementares que atendam às suas necessidades 🚀

**Por que é importante olhar para este dado?**

Para empresas que oferecem serviços recorrentes, monitorar e otimizar o Cross-sell é crucial por várias razões:

1. **Aumento da Receita** : Oferecer produtos ou serviços adicionais pode aumentar significativamente a receita sem a necessidade de adquirir novos clientes.
2. **Melhoria na Satisfação do Cliente** : Oferecer soluções complementares que agreguem valor pode aumentar a satisfação e a lealdade do cliente.
3. **Maior Valor Vitalício do Cliente (LTV)** : Clientes que fazem cross-sell geralmente permanecem mais tempo e gastam mais, aumentando o LTV.

**Exemplos**

* **SaaS** : Uma plataforma de gerenciamento de projetos oferece um serviço básico de gestão de tarefas e, como Cross-sell, oferece serviços adicionais como armazenamento na nuvem, integração com outras ferramentas e relatórios avançados.
* **Contabilidades** : Um escritório de contabilidade oferece um serviço básico de preparação de impostos e, como Cross-sell, oferece consultoria financeira, planejamento tributário e serviços de auditoria.

## Como ver o Cross-sell no Conexa?

É simples! basta adicionar o widget acessando a Página Inicial (Dashboard) > Personalizar Tela Inicial e Selecionar o widget de Cross-sell.

[![](https://downloads.intercomcdn.com/i/o/1136906379/906669dceed5166c87e1adb5/image.png?expires=1751314500&signature=b7ec744f291d3f3292112b1ae59bb9b0190047b625633c0c09e8bfbd4028f6dd&req=dSEkEMB%2Bm4JYUPMW1HO4zWW8efsjGxOLx96N%2F6JH%2BFN2tYXR71AMQ8Ueikv7%0Al%2FfnLPyL08qxfX7s%2Fts%3D%0A)](https://downloads.intercomcdn.com/i/o/1136906379/906669dceed5166c87e1adb5/image.png?expires=1751314500&signature=b7ec744f291d3f3292112b1ae59bb9b0190047b625633c0c09e8bfbd4028f6dd&req=dSEkEMB%2Bm4JYUPMW1HO4zWW8efsjGxOLx96N%2F6JH%2BFN2tYXR71AMQ8Ueikv7%0Al%2FfnLPyL08qxfX7s%2Fts%3D%0A)

## Como o Cross-sell é calculado no Conexa?

 **Condições para Considerar um Cross-sell** :

* Os clientes precisam ter sido cadastrados com data menor que o mês em questão.

  * *Essa condição é criada para que sejam selecionados somente clientes que já são "da casa".*
* Deve haver um novo contrato ou venda recorrente dentro do mês em questão.
* Não contabilizamos vendas recorrentes ou contratos que aconteceram no dia do primeiro contrato.

  * *Isso é feito para evitar que os dados não sejam comprometidos por novos clientes que já contratam com serviços complementares (vendas recorrentes).              *

**Exemplificação da Regra**

Para facilitar o entendimento, vejamos um exemplo prático:

* **Cliente X** : Teve seu contrato iniciado em Janeiro. Em Fevereiro, ele adquiriu um módulo opcional (venda recorrente) de R$ 200 / mês.
* **Cálculo** : Este valor será contabilizado como Cross-sell.
* **Cliente Y** : Teve seu contrato iniciado em Fevereiro, junto com 2 vendas recorrentes (serviços complementares), totalizando R$ 400 / mês.
* **Cálculo** : Este valor **não** será contabilizado como Cross-sell, mas sim como [New MRR](https://ajuda.conexa.app/pt/articles/9289616-widget-de-new-mrr).
* **Cliente Z:**  Teve seu contrato iniciado em Janeiro. Em Fevereiro, ele adquiriu um novo serviço (novo contrato) de R$ 500 / mês.

  * **Cálculo** : Este valor será contabilizado como Cross-sell.

O widget de cross-sell no Conexa somará as mensalidades que entram na condição (R$ 200 + R$ 500) e exibirá o total de R$ 700 como valor de Cross-sell para o mês de Fevereiro.

## Conclusão

O widget de Cross-sell do Conexa é uma ferramenta valiosa para empresas que oferecem serviços recorrentes monitorarem e gerirem suas receitas. Ao entender e utilizar corretamente as regras de cálculo de Cross-sell, as empresas podem identificar oportunidades de aumento de receita e satisfação do cliente, oferecendo produtos e serviços adicionais que atendam às necessidades dos seus clientes. 🤝
