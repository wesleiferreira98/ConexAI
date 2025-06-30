# Entendendo o Cálculo do Churn Rate Total e Médio no Conexa

No Conexa, o churn rate, que mede a taxa de cancelamento de clientes, é calculado de duas formas: o churn rate total e o churn rate médio. Embora ambos os cálculos tenham o objetivo de mensurar a rotatividade dos clientes, as fórmulas utilizadas são diferentes. Vamos entender como cada um é calculado no artigo a seguir!

**1. Churn Rate Total**

**Fórmula:**

```
Churn Rate Total = (Total de Cancelamentos no Período) / (Quantidade de Clientes Ativos no Início do Período) * 100
```

O Churn Rate Total fornece uma visão geral da taxa de cancelamento em relação ao número de clientes que a empresa tinha no início do período. Essa fórmula é útil para entender o impacto total dos cancelamentos durante o período em análise.

Por exemplo, se no início do ano uma empresa tinha 100 clientes e, ao longo do ano, 20 deles cancelaram o serviço, o Churn Rate Total seria de 20% (20/100*100). Isso mostra a proporção de clientes que foram perdidos em relação à base inicial de clientes.

**2. Média do Churn Rate**

[![](https://downloads.intercomcdn.com/i/o/yei38q6d/1216932488/19cfb0994a9ca6aa532b74472bdb/image.png?expires=1751311800&signature=b76cd01250a37c47341da16bebc1a4097a5a441bb85dbc556e77eb8211119d72&req=dSImEMB9n4VXUfMW1HO4zQFWinzLHX1liEe0%2FzEYpfHT6l8UcEzHaZKa1Ohf%0ALyzPcpBESxfjOr6Nl3g%3D%0A)](https://downloads.intercomcdn.com/i/o/yei38q6d/1216932488/19cfb0994a9ca6aa532b74472bdb/image.png?expires=1751311800&signature=b76cd01250a37c47341da16bebc1a4097a5a441bb85dbc556e77eb8211119d72&req=dSImEMB9n4VXUfMW1HO4zQFWinzLHX1liEe0%2FzEYpfHT6l8UcEzHaZKa1Ohf%0ALyzPcpBESxfjOr6Nl3g%3D%0A)

**Fórmula:**

```
Média do Churn Rate = (Soma de Todos os Valores de Churn Rate do Período) / (Quantidade de Meses no Período)
```

Nesse caso, o cálculo é feito somando os valores de Churn Rate de cada mês e dividindo pelo número de meses analisados. Essa abordagem oferece uma visão mais granular, já que considera a variação mensal na taxa de cancelamento e reflete a média ao longo do tempo.

Por exemplo, se a empresa teve os seguintes Churn Rates mensais em três meses consecutivos: 5%, 10% e 8%, a média do Churn Rate seria 7.67% (23%/3). Esse cálculo oferece uma forma de visualizar a tendência do Churn ao longo do tempo e permite uma análise mais sensível a oscilações mensais.

**Por que as Fórmulas São Diferentes?**

As fórmulas para calcular o Churn Rate Total e o Churn Rate médio são diferentes porque cada uma reflete uma perspectiva distinta sobre o comportamento dos cancelamentos.

1. **Churn Rate Total** : Focado no impacto geral, essa fórmula mede a porcentagem de perda com base no tamanho original da base de clientes no início do período. É útil para ter uma visão macro e entender quanto a empresa perdeu em termos de clientes ao longo do tempo.
2. **Média do Churn Rate** : Esse cálculo ajuda a suavizar as variações mensais, fornecendo uma métrica que indica o desempenho médio durante o período. Ao analisar essa média, é possível identificar tendências e padrões que não seriam tão evidentes apenas olhando para o churn total.

Ambos os métodos são importantes para avaliar a saúde da base de clientes e tomar decisões informadas para reduzir o churn!

* **A mesma lógica apresentada neste artigo também é aplicada ao MRR Churn Rate Total e MRR Churn Rate Médio**
* Caso o filtro de "Clientes adquiridos em" esteja ativo, o Churn Rate total é calculado com base na população total do cohort:

  * ```
    Churn Rate Total (com cohort) = (Total de Cancelamentos no Período) / (Quantidade Total de Clientes do Cohort) * 100
    ```
  * Isto é feito porque, como a população é fixa, a análise é feita tendo como referência a população do cohort.
