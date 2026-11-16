// Repository-owned reference application; fixture identity is separate from candidates.
export function initial() { return {version: 1, next: 1, entries: []}; }
export function restore(text) {
  if (!text) return initial();
  try {
    const state = JSON.parse(text);
    if (state.version !== 1 || !Number.isSafeInteger(state.next) || state.next < 1 ||
        !Array.isArray(state.entries) || state.entries.some(item =>
          !Number.isSafeInteger(item.id) || item.id < 1 || typeof item.name !== 'string' ||
          typeof item.tag !== 'string' || !Number.isInteger(item.quantity) || item.quantity < 1 || item.quantity > 99) ||
        new Set(state.entries.map(item => item.id)).size !== state.entries.length ||
        state.entries.some(item => item.id >= state.next)) return initial();
    return state;
  } catch { return initial(); }
}
export function change(state, action) {
  const next = structuredClone(state);
  if (action.type === 'add') {
    const name = String(action.name ?? '').trim(), tag = String(action.tag ?? '').trim() || '未分类';
    const quantity = Number(action.quantity);
    if (!name) throw new Error('请填写名称');
    if (name.length > 32) throw new Error('名称最多32个字符');
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 99) throw new Error('数量须为1至99的整数');
    if (next.entries.some(item => item.name.toLocaleLowerCase('en-US') === name.toLocaleLowerCase('en-US') && item.tag === tag))
      throw new Error('该分类中已有同名条目');
    next.entries.push({id: next.next++, name, tag, quantity});
  } else if (action.type === 'remove') {
    if (!next.entries.some(item => item.id === action.id)) throw new Error('条目不存在');
    next.entries = next.entries.filter(item => item.id !== action.id);
  } else if (action.type === 'clear') { return initial(); }
  else throw new Error('未知操作');
  return next;
}
export function view(state, query = '', order = 'newest') {
  const needle = String(query).trim().toLocaleLowerCase('en-US');
  const entries = state.entries.filter(item => `${item.name}\n${item.tag}`.toLocaleLowerCase('en-US').includes(needle));
  if (order === 'name') entries.sort((a,b) => a.name.localeCompare(b.name, 'zh-CN') || a.id - b.id);
  else entries.sort((a,b) => b.id - a.id);
  return {entries, items: entries.length, quantity: entries.reduce((total,item) => total + item.quantity, 0)};
}
