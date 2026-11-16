// Independent collection model, reconstructed from the reviewed behavior contract.
export const initial = () => ({version: 1, next: 1, entries: []});

const positiveSafe = value => Number.isSafeInteger(value) && value >= 1;
const validQuantity = value => Number.isInteger(value) && value >= 1 && value <= 99;
const fold = value => value.toLocaleLowerCase('en-US');

export function restore(serialized) {
  if (!serialized) return initial();
  try {
    const value = JSON.parse(serialized);
    if (value.version !== 1 || !positiveSafe(value.next) || !Array.isArray(value.entries)) return initial();
    const seen = new Set();
    for (const item of value.entries) {
      if (!positiveSafe(item.id) || item.id >= value.next || seen.has(item.id) ||
          typeof item.name !== 'string' || typeof item.tag !== 'string' || !validQuantity(item.quantity)) return initial();
      seen.add(item.id);
    }
    return value;
  } catch {
    return initial();
  }
}

export function change(collection, command) {
  const result = structuredClone(collection);
  switch (command.type) {
    case 'add': {
      const title = String(command.name ?? '').trim();
      const category = String(command.tag ?? '').trim() || '未分类';
      const amount = Number(command.quantity);
      if (title.length === 0) throw new Error('请填写名称');
      if (title.length > 32) throw new Error('名称最多32个字符');
      if (!validQuantity(amount)) throw new Error('数量须为1至99的整数');
      const collision = result.entries.find(entry => fold(entry.name) === fold(title) && entry.tag === category);
      if (collision) throw new Error('该分类中已有同名条目');
      const entry = {id: result.next, name: title, tag: category, quantity: amount};
      result.next += 1;
      result.entries.push(entry);
      return result;
    }
    case 'remove': {
      const index = result.entries.findIndex(entry => entry.id === command.id);
      if (index < 0) throw new Error('条目不存在');
      result.entries.splice(index, 1);
      return result;
    }
    case 'clear': return initial();
    default: throw new Error('未知操作');
  }
}

export function view(collection, query = '', order = 'newest') {
  const search = fold(String(query).trim());
  const visible = [];
  for (const entry of collection.entries) {
    if (fold(entry.name + '\n' + entry.tag).includes(search)) visible.push(entry);
  }
  const compare = order === 'name'
    ? (left, right) => left.name.localeCompare(right.name, 'zh-CN') || left.id - right.id
    : (left, right) => right.id - left.id;
  visible.sort(compare);
  let total = 0;
  for (const entry of visible) total += entry.quantity;
  return {entries: visible, items: visible.length, quantity: total};
}
