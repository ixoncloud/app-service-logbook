import { writable } from 'svelte/store';
import type { BackendComponentClient } from '@ixon-cdk/types';
import type { Note } from './types';

export class NotesService {
  notes = writable<Note[]>([]);
  loaded = writable<boolean>(false);

  constructor(private client: BackendComponentClient) {}

  add(text: string, subject?: string, category?: number) {
    return this.client.call('notes.add', { text, subject, category }).then(result => {
      if (result.data.success) {
        this.notes.update(note => [result.data.data, ...note]);
      }
    });
  }

  edit(id: string, text: string, subject?: string, category?: number | null) {
    return this.client.call('notes.edit', { note_id: id, text, subject, category }).then(result => {
      if (result.data.success) {
        this.notes.update(notes => notes.map(note => (note._id === id ? { ...note, ...result.data.data } : note)));
      }
      // The entry list is refreshed whenever a user modifies (or tried to modify) an entry.
      this.load();
    });
  }

  load() {
    return this.client.call('notes.get').then(result => {
      if (result.data.success) {
        this.notes.set(result.data.data);
      }
      this.loaded.set(true);
    });
  }

  remove(id: string) {
    this.notes.update(notes => notes.filter(note => note._id !== id));
    return this.client.call('notes.remove', { note_id: id });
  }
}
