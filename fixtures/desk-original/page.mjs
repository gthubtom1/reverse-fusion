import {initial, restore, change, view} from './core.mjs';
const $ = id => document.getElementById(id), key = 'rf-owned-desk-v1';
let state = restore(localStorage.getItem(key));
function render() {
  const result = view(state, $('query').value, $('order').value);
  $('rows').replaceChildren();
  for (const item of result.entries) {
    const row = document.createElement('tr');
    for (const value of [item.name,item.tag,item.quantity]) {
      const cell = document.createElement('td'); cell.textContent = value; row.append(cell);
    }
    const cell = document.createElement('td'), button = document.createElement('button');
    button.className = 'remove'; button.textContent = '删除'; button.type = 'button';
    button.addEventListener('click', () => update({type:'remove',id:item.id}));
    cell.append(button); row.append(cell); $('rows').append(row);
  }
  $('empty').hidden = result.items !== 0;
  $('empty').textContent = state.entries.length ? '没有匹配的条目。' : '还没有条目，先添加一个吧。';
  $('summary').textContent = `${result.items} 项 · 共 ${result.quantity} 件`;
}
function update(action) {
  try {
    const next = change(state, action);
    localStorage.setItem(key, JSON.stringify(next)); state = next; $('error').textContent = ''; render();
    return true;
  } catch (error) { $('error').textContent = error.message; return false; }
}
$('add').addEventListener('submit', event => {
  event.preventDefault();
  if (update({type:'add',name:$('name').value,tag:$('tag').value,quantity:$('quantity').value})) {
    $('name').value = ''; $('name').focus();
  }
});
$('query').addEventListener('input', render); $('order').addEventListener('change', render);
$('clear').addEventListener('click', () => { if (confirm('确定清空全部条目吗？')) update({type:'clear'}); });
render();
