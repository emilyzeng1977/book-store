def serialize_book(book):
    if '_id' in book:
        book['_id'] = str(book['_id'])
    return book