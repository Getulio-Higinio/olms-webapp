from olms_app.db.models import AuditLog

def log_action(session, action, entity, entity_id="", details="", user="system"):
    session.add(AuditLog(
        user=user,
        action=action,
        entity=entity,
        entity_id=str(entity_id),
        details=details
    ))
    session.commit()
