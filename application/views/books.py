'''views/books.py'''
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required, jwt_refresh_token_required, get_jwt_claims, get_jwt_identity)
from application import BookModel

class Books(Resource):
    '''retrieve all books'''

    def get(self):
        '''method ['GET']'''
        all_books = {}
        result = BookModel.query.all()
        for book in result:
            all_books[book.book_id] = {"title": book.title, "author": book.author,
                                       "edition": book.edition, "copies": book.copies, "status": book.status}

        return all_books, 200

    @jwt_required
    def post(self):
        '''Only admin can add a book'''
        claims = get_jwt_claims()

        if claims["admin"] is True:
            data = request.get_json()
            if not data:
                return {"message": "Fields cannot be empty"}, 400

            title = data.get('title')
            author = data.get('author')
            edition = data.get('edition')
            copies = data.get('copies')

            my_list = [title, author, edition, copies]
            for i in my_list:
                if i is None or not i:
                    return {"message": "title, author, edition or copies fields missing"}, 400
            my_list = [title, author, edition]
            for i in my_list:
                i = i.strip()
                if not i:
                    return {"message": "Enter valid data"}, 400

            if not isinstance(copies, int):
                return {"message": "Field copies has to be an integer"}, 400
            if copies < 0:
                return {"message": "Copies entered cannot be a negative number"}, 400
            if copies == 0:
                status = "unavailable"
            status = "available"

            if BookModel.query.filter_by(title=title).first():
                return {"message": "Add book failed. Book title already exists"}, 409
            my_book = BookModel(author, title, edition, copies, status)
            my_book.save()
            return {"message": "Book successfully added"}, 201
        return {"message": "Admin privilege required"}, 403


class BooksBookId(Resource):
    '''class representing book by id actions'''

    def get(self, book_id):
        '''retrieve a single book'''
        book = BookModel.query.filter_by(book_id=book_id).first()
        if book is None:
            return {"message": "Book doesn't exist"}, 404
        return {book.book_id: {"title": book.title, "author": book.author,
                               "edition": book.edition, "copies": book.copies, "status": book.status}}, 200

    @jwt_required
    def put(self, book_id):
        '''Only admin can edit a book'''
        claims = get_jwt_claims()
        if claims["admin"] is True:
            data = request.get_json()
            if not data:
                return {"message": "Enter valid data for edit"}, 400
            title = data.get("title")
            author = data.get("author")
            edition = data.get("edition")
            copies = data.get("copies")
            status = data.get("status")

            book = BookModel.query.filter_by(book_id=book_id).first()
            if book is None:
                return dict(message="book doesn't exist"), 404
            if not title and not author and not edition and not copies and not status:
                return dict(message="all fields cannot be empty enter data to edit"), 400
            if not title:
                title = book.title
            if not author:
                author = book.author
            if not edition:
                edition = book.edition
            if not copies:
                copies = book.copies
            if not status:
                status = book.status

            my_list = [title, edition, author, status]
            for i in my_list:
                i = i.strip()
                if i is None or not i:
                    return dict(message="Enter vaild data"), 400

            if not isinstance(copies, int):
                return {"message": "Field copies has to be an integer"}, 400
            if copies < 0:
                return {"message": "Copies entered cannot be a negative number"}, 400
            status = status.encode('ascii')
            if status == "available" or status == "unavailable":
                book.title = title
                book.author = author
                book.edition = edition
                book.copies = copies
                book.status = status
                book.save()
                return dict(message="Book {} successfully edited".format(book_id)), 200

            return dict(message="status has to be either available or unavailble", status=title), 400
        return {"message": "Admin privilege required"}, 403

    @jwt_required
    def delete(self, book_id):
        '''Only admin can delete a book'''
        claims = get_jwt_claims()
        if claims["admin"] is True:
            book = BookModel.query.filter_by(book_id=book_id).first()
            if book is None:
                return {"message": "book {} doesn't exist".format(book_id)}, 404
            book.delete()
            return {"message": "book {} deleted successfully".format(book_id)}, 200

        return {"message": "Admin privilege required"}, 403