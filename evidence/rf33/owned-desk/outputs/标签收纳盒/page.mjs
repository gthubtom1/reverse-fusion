// Independent browser controller. All data stays in this browser's local storage.
import {restore, change, view} from './core.mjs';

const controls = Object.fromEntries(['add', 'name', 'tag', 'quantity', 'error', 'query', 'order', 'rows', 'empty', 'summary', 'clear']
  .map(id => [id, document.getElementById(id)]));
const storageKey = 'rf-owned-desk-v1';
let collection = restore(localStorage.getItem(storageKey));

function paint() {
  const visible = view(collection, controls.query.value, controls.order.value);
  const rows = visible.entries.map(entry => {
    const tr = document.createElement('tr');
    for (const text of [entry.name, entry.tag, entry.quantity]) {
      const td = document.createElement('td');
      td.textContent = text;
      tr.append(td);
    }
    const action = document.createElement('td');
    const remove = document.createElement('button');
    remove.type = 'button';
    remove.className = 'remove';
    remove.textContent = '删除';
    remove.onclick = () => commit({type: 'remove', id: entry.id});
    action.append(remove);
    tr.append(action);
    return tr;
  });
  controls.rows.replaceChildren(...rows);
  controls.empty.hidden = visible.items !== 0;
  controls.empty.textContent = collection.entries.length === 0 ? '还没有条目，先添加一个吧。' : '没有匹配的条目。';
  controls.summary.textContent = `${visible.items} 项 · 共 ${visible.quantity} 件`;
}

function commit(command) {
  try {
    const updated = change(collection, command);
    localStorage.setItem(storageKey, JSON.stringify(updated));
    collection = updated;
    controls.error.textContent = '';
    paint();
    return true;
  } catch (failure) {
    controls.error.textContent = failure.message;
    return false;
  }
}

controls.add.onsubmit = event => {
  event.preventDefault();
  const success = commit({type: 'add', name: controls.name.value, tag: controls.tag.value, quantity: controls.quantity.value});
  if (success) {
    controls.name.value = '';
    controls.name.focus();
  }
};
controls.query.oninput = paint;
controls.order.onchange = paint;
controls.clear.onclick = () => {
  if (window.confirm('确定清空全部条目吗？')) commit({type: 'clear'});
};
paint();
