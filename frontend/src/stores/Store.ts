import { reactive } from "vue";

/**
 * store class responsible for holding type related data across the vue app instance.
 */
export default class Store<T extends Record<any, any>> {
  private readonly data: T;
  private readonly emptyData: T;

  constructor(state: T, emptyState?: T) {
    this.data = reactive(state) as T;

    if (emptyState != null) {
      // make a "copy" of the empty object
      this.emptyData = JSON.parse(JSON.stringify(emptyState));
    } else {
      this.emptyData = JSON.parse(JSON.stringify(state));
    }
  }

  get state(): T {
    return this.data;
  }

  set state(state: T) {
    const stateEntries = (Object.entries(state) as [keyof T, T[keyof T]][]);

    for (const [key, value] of stateEntries) {
      this.data[key] = value;
    }
  }

  is(state: T) {
    const stateEntries = (Object.entries(state) as [keyof T, T[keyof T]][]);

    for (const [key, value] of stateEntries) {
      if (value != this.data[key]) {
        return false;
      }
    }

    return true;
  }

  empty() {
    this.state = this.emptyData;
  }

  isEmpty() {
    return this.is(this.emptyData);
  }
}
