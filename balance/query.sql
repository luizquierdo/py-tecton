select a.parent, a.credit, a.debit, e.docstatus 
from `tabJournal Entry Account` a, `tabJournal Entry` e 
where account = '2.1.2.1 Provision Existencias No Facturadas - COHH' 
and a.parent = e.name and e.posting_date > '2016-01-01' 
and e.docstatus = 1

select account, round(sum(debit)) as debitos, round(sum(credit)) as creditos, round((sum(debit) - sum(credit))) as saldo 
from `tabGL Entry` 
where company = 'Consorcio HLI Hydrogroup SpA' 
group by account;


select g.account, round(sum(g.debit)) as debitos, round(sum(g.credit)) as creditos, round((sum(g.debit) - sum(g.credit))) as saldo 
from `tabGL Entry` g, tabAccount a 
where a.name = g.account 
and g.company = 'Consorcio HLI Hydrogroup SpA' 
and g.docstatus = 1 
and g.posting_date <= '2015-12-31'
and g.posting_date > '2014-12-31'
group by g.account order by g.account, a.root_type;