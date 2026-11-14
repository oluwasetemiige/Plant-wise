from app import db
from app.utils import normalize_phone


def test_normalize_phone():
    assert normalize_phone("0801 234 5678") == "2348012345678"
    assert normalize_phone("+234 801 234 5678") == "2348012345678"


def test_farmer_and_history(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "t.db"))
    db.init()
    assert db.get_farmer("234801") is None
    db.save_farmer("234801", city="Kano")
    assert db.get_farmer("234801")["subscribed"] == 0
    db.save_farmer("234801", subscribed=1)
    f = db.get_farmer("234801")
    assert f["city"] == "Kano" and f["crop"] == "maize" and f["subscribed"] == 1
    assert [x["phone"] for x in db.list_subscribed()] == ["234801"]
    db.add_message("234801", "user", "hi")
    db.add_message("234801", "assistant", "hello")
    assert [m["role"] for m in db.recent_messages("234801")] == ["user", "assistant"]
