# Los modelos de compras (PurchaseOrder, PurchaseOrderItem, Supplier)
# residen en la app 'inventory' para mantener compatibilidad con la BD existente.
# Esta app 'purchasing' actúa como capa de presentación y negocio,
# importando directamente desde inventory.models.
# En una futura refactorización mayor, los modelos podrán migrarse aquí.
