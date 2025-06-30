# Relatório LTV no Conexa

# O que é LTV?

O LTV (Lifetime Value) é uma estimativa do valor total que um cliente gera de receita para uma empresa ao longo da sua relação com ela. É uma métrica muito importante, principalmente quando analisada em conjunto com o [CAC](https://ajuda.conexa.app/pt/articles/7321519-relatorio-de-cac-no-conexa) (Custo de Aquisição de Clientes).

# Como calcular o LTV?

Para entender como calcular o LTV, segue um exemplo: vamos imaginar que você cobra R$  100,00 por mês de um cliente e que ele manteve este contrato por um período de 12 meses. Neste caso, o LTV dele seria de R$ 100,00 x 12 = R$1200.

Este exemplo foi para o cálculo de LTV de somente um cliente, vamos analisar então como funciona o cálculo para mais que um cliente. Para detalhar um pouco melhor o método que Conexa utiliza para realizar este cálculo, antes precisamos conhecer duas outras métricas:

* **ARPU (Average Revenue Per User)**

  * ARPU é a receita média por usuário. Este valor é obtido pela seguinte fórmula: *ARPU  = Receitas operacionais do mês / *total de clientes ativos do** **mês**
  * *Cliente ativo para este cálculo é qualquer cliente com status ativo e que possua contrato ativo, venda recorrente ativa ou consumiu pelo menos alguma venda (maior que zero no mês)*
* **Churn rate**

  * É o Total de clientes cancelados dividido pelo número total de clientes ativos do último mês. [Saiba mais sobre o Churn rate neste artigo](https://ajuda.conexa.app/pt/articles/5277443-relatorio-churn-o-que-e-e-pra-que-serve).

Com essas informações, chegamos na fórmula para calcular o LTV:

**LTV  = ARPU / Churn Rate**

Na fórmula acima, temos **1 / Churn Rate **como uma estimativa para o tempo de relacionamento médio dos clientes com a empresa. Ela leva em consideração que, caso o taxa de cancelamento aumente, o tempo de relacionamento vai diminuir.

# Como verifica o LTV no Conexa?

Na tela inicial do Conexa, clique no botão "Personalizar Dashboard" e,  a seguir, "Adicionar widget".  Na próxima tela, selecione o widget de LTV:

[![](https://downloads.intercomcdn.com/i/o/789688999/26947f113bd5e6fb7548aec0/Screen+Shot+2023-07-20+at+16.11.48.png?expires=1751310000&signature=29cd071ae6482bf476dd98ec6a971d9a807e85e61f29fbadb22c3d98c07a1804&req=cyguEMF2lIhWFb4f3HP0gEvC695uZIgDQMx%2FAJpldn5ZPaTsP7jUXKU7JGnQ%0AZM8zzhsbA2IbXhTUQg%3D%3D%0A)](https://downloads.intercomcdn.com/i/o/789688999/26947f113bd5e6fb7548aec0/Screen+Shot+2023-07-20+at+16.11.48.png?expires=1751310000&signature=29cd071ae6482bf476dd98ec6a971d9a807e85e61f29fbadb22c3d98c07a1804&req=cyguEMF2lIhWFb4f3HP0gEvC695uZIgDQMx%2FAJpldn5ZPaTsP7jUXKU7JGnQ%0AZM8zzhsbA2IbXhTUQg%3D%3D%0A)

[![](https://downloads.intercomcdn.com/i/o/789690173/48e346360cc2fc138b83c9f7/Screen+Shot+2023-07-20+at+16.13.07.png?expires=1751310000&signature=f7956e3574d32529abd6a5613ef26f1a26f24321e8eba63908d5c0205b59aa87&req=cyguEMB%2BnIZcFb4f3HP0gJpZ3YzMqLIfKf3BairC6XgNNw14L9buAWoekYq7%0A%2F4q%2FAQlZsPcQSO9Dqg%3D%3D%0A)](https://downloads.intercomcdn.com/i/o/789690173/48e346360cc2fc138b83c9f7/Screen+Shot+2023-07-20+at+16.13.07.png?expires=1751310000&signature=f7956e3574d32529abd6a5613ef26f1a26f24321e8eba63908d5c0205b59aa87&req=cyguEMB%2BnIZcFb4f3HP0gJpZ3YzMqLIfKf3BairC6XgNNw14L9buAWoekYq7%0A%2F4q%2FAQlZsPcQSO9Dqg%3D%3D%0A)

A seguir, localize o seu mais novo widget na sua tela inicial!

[![](https://downloads.intercomcdn.com/i/o/789690360/3bf6649cef2e0d6c4b6614b8/Screen+Shot+2023-07-20+at+16.13.42.png?expires=1751310000&signature=040ede65fff471648fad72a224cd5bc4e4fa4aad8ac2ec8c3fc287c54dbca5e2&req=cyguEMB%2BnodfFb4f3HP0gIIvuWN28Sbwd4YmPjgPHNdfveKtLYm8%2B%2BEDbcQx%0A6qfg3hCywqyCnDodQw%3D%3D%0A)](https://downloads.intercomcdn.com/i/o/789690360/3bf6649cef2e0d6c4b6614b8/Screen+Shot+2023-07-20+at+16.13.42.png?expires=1751310000&signature=040ede65fff471648fad72a224cd5bc4e4fa4aad8ac2ec8c3fc287c54dbca5e2&req=cyguEMB%2BnodfFb4f3HP0gIIvuWN28Sbwd4YmPjgPHNdfveKtLYm8%2B%2BEDbcQx%0A6qfg3hCywqyCnDodQw%3D%3D%0A)

 **⚠️ Pontos importantes**

* Como a fórmula do LTV utiliza o Churn Rate (que é uma porcentagem), os resultados podem oscilar, principalmente caso o número de clientes ativos seja pequeno.
* Além disso, por utilizar o Churn Rate, o widget só exibe o LTV de meses anteriores ao mês atual. Para evitar situações como início do mês, em que não ocorreu ainda nenhum cancelamento.
* Caso o widget de LTV não apareça, entre em contato com algum administrador do sistema.

---
