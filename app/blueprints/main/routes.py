from app import db as main
from flask import render_template, request, flash, redirect, make_response, g
from app.blueprints.auth.auth import token_auth
from flask.helpers import url_for
import requests
from app.models import User, Item
from . forms import CreateItemsForm, EditItemsForm
from flask_login import login_required, current_user
from .import bp as main

@main.route('/', methods=['GET'])
@login_required
def index():
    all_items = Item.query.all()
    items = [item.to_dict() for item in all_items]
    return render_template('index.html.j2', items=items)
    

@main.route('/market/<int:category_id>', methods=['GET'])
@login_required
def market(category_id):
    all_items = Item.query.filter_by(category_id = category_id).all()
    items = [item.to_dict() for item in all_items]
    return render_template('market.html.j2', category_id=category_id, items=items)


@main.route('/view_item/<int:id>', methods=['GET'])
@login_required
def view_item(id):
    item = Item.query.get(id).to_dict()
    return render_template('view_item.html.j2', item=item)


@main.route('/create_item/<int:category_id>', methods=['GET', 'POST'])
@login_required
def create_item(category_id):
    if current_user.is_admin==False:
        return redirect(url_for('main.market', category_id=category_id))
    
    form = CreateItemsForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_item_data = {
                "name":form.name.data,
                "price":form.price.data,
                "img":form.img.data,
                "description":form.description.data,
                "category_id":category_id,
                "owner":current_user.id
            }
            #create and empty item
            new_item_object = Item()
            # build item with form data
            new_item_object.from_dict(new_item_data)
            # save item to database
            new_item_object.save()
            flash('item added', 'success')
        except:
            error_string = "There was an unexpected Error creating the item. Please Try again."
            flash(error_string)
            return render_template('create_item.html.j2',form=form, error = error_string)
        return redirect(url_for('main.market', category_id=category_id ))
    return render_template('create_item.html.j2', form = form)


@main.route('/edit_item/<int:id>', methods=['GET','POST'])
@login_required
def edit_item(id):
    form = EditItemsForm()
    item=Item.query.get(id)
    
    # if not form.is_submitted():
    if request.method == 'GET':
        form = EditItemsForm()
        form.name.data = item.name
        form.price.data = item.price
        form.img.data = item.img
        form.description.data = item.description
    # else:
    #     form = EditItemsForm() 

    if request.method == 'POST' and form.validate_on_submit():
        edited_item_data = {
            "name":form.name.data,
            "price":form.price.data,
            "img":form.img.data,
            "description":form.description.data,
        }
        
        try:
            item.from_dict(edited_item_data)
            item.save()
            flash('item edited', 'success')
        except:
            flash('There was an unexpected error', 'danger')
            return redirect(url_for('main.edit_item'))
        return redirect(url_for('main.market', category_id=item.category_id))
    return render_template('edit_item.html.j2', form = form)


@main.route('/delete_item/<int:id>', methods=['GET','POST'])
@login_required
def delete_item(id):
    if current_user.is_admin == False:
        return redirect(url_for('main.market'))
    if request.method == 'POST':
        item_to_delete = Item.query.get(id)
        categoryid = item_to_delete.category_id
        item_to_delete.delete()
        flash(f'{item_to_delete.name} was deleted', 'info')
        return redirect(url_for('main.market', category_id=categoryid))
    
    
@main.route('/add_item/<int:id>', methods=['GET','POST'])
@login_required
def add_item(id):
    if request.method == 'POST':
        item_to_add = Item.query.get(id)
        item_to_add.add_to_cart(user=current_user)
        flash(f'{item_to_add.name} was added to your cart', 'info')
        return redirect(url_for('main.market', category_id=item_to_add.category_id))


@main.route('/remove_cart_item<int:id>', methods=['GET', 'POST'])
@login_required
def remove_cart_item(id):
    # for item in Item.query.filter_by(owner=current_user.id):
    print(id)
    for item in Item.query.filter_by(id=id):
        item_to_remove = item.name
        categoryid = item.category_id
        item.remove_from_cart()
        flash(f'{item_to_remove} was removed from the cart', 'info')
        return redirect(url_for('main.market', category_id=categoryid))


@main.route('/remove_all_cart_items', methods=['GET', 'POST'])
@login_required
def remove_all_cart_items():
    for item in Item.query.filter_by(owner=current_user.id):
        categoryid = item.category_id
        item.empty_cart()
    flash("All the items were removed from the cart", 'info')    
    return redirect(url_for('main.market', category_id=categoryid))