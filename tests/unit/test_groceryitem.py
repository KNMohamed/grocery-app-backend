from domain.models import GroceryItem, ItemStatus

    
def test_marked_as_purchased():
    apples = GroceryItem("Apples", 5)
    assert apples.status is ItemStatus.PENDING
    apples.mark_as_purchased()
    assert apples.status is ItemStatus.PURCHASED
    
def test_marked_as_pending():
    apples = GroceryItem("Apples", 5)
    apples.mark_as_purchased()
    assert apples.status is ItemStatus.PURCHASED
    apples.mark_as_pending()
    assert apples.status is ItemStatus.PENDING