from domain.models import GroceryItem, ItemStatus

    
def test_marked_as_purchased():
    apples = GroceryItem("Apples", 5)
    assert apples.status is ItemStatus.PENDING
    assert apples.purchased_at is None
    apples.mark_as_purchased()
    assert apples.status is ItemStatus.PURCHASED
    assert apples.purchased_at is not None
    
def test_marked_as_pending():
    apples = GroceryItem("Apples", 5)
    apples.mark_as_purchased()
    assert apples.status is ItemStatus.PURCHASED
    apples.mark_as_pending()
    assert apples.status is ItemStatus.PENDING