locals {
  rules_file = yamldecode(file("${path.module}/../rules/datacenter-atl.yml"))
  rules      = local.rules_file.rules

  nsg_rules = {
    for i, r in local.rules : r.name => {
      priority    = 100 + i * 10
      access      = r.action == "allow" ? "Allow" : "Deny"
      protocols   = distinct([for s in r.service : split("-", s)[0]])
      ports       = distinct([for s in r.service : split("-", s)[1]])
      source      = r.source
      destination = r.destination
    }
  }
}

resource "azurerm_resource_group" "fw" {
  name     = "rg-fw-policy-lab"
  location = "eastus"
}
resource "azurerm_network_security_group" "atl" {
  name                = "nsg-atl-dc"
  location            = azurerm_resource_group.fw.location
  resource_group_name = azurerm_resource_group.fw.name
}
resource "azurerm_network_security_rule" "rule" {
  for_each = local.nsg_rules

  name                         = each.key
  priority                     = each.value.priority
  direction                    = "Inbound"
  access                       = each.value.access
  protocol                     = length(each.value.protocols) == 1 ? title(each.value.protocols[0]) : "*"
  source_port_range            = "*"
  destination_port_ranges      = each.value.ports
  source_address_prefixes      = each.value.source
  destination_address_prefixes = each.value.destination
  resource_group_name          = azurerm_resource_group.fw.name
  network_security_group_name  = azurerm_network_security_group.atl.name
}
