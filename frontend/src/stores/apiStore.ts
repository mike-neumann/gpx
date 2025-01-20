import Store from "stores/Store";
import { ApiStore } from "src/types/types";

export const apiStore = new Store<ApiStore>({
  drivers: [],
  vehicles: []
});
