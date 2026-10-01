/* Locally authored inspection tool. No network calls. Does not write source models. */
(function () {
  const fs = require('fs');
  const path = require('path');
  let input;
  function choose(run) {
    Blockbench.import({extensions:['json'],type:'Senra audit specification',readtype:'text'}, files => {
      if (!files.length) return; input=files[0].path;
      run().catch(error => Blockbench.showMessageBox({title:'Audit failed',message:String(error.stack || error)}));
    });
  }
  let action;
  let heldAction;
  async function audit() {
    const spec = JSON.parse(fs.readFileSync(input, 'utf8'));
    const expectedOut = path.dirname(input) + '/native-blockbench';
    if (spec.output_root !== expectedOut) throw new Error('Unexpected output root');
    fs.mkdirSync(expectedOut, {recursive: true});
    const results = [];
    for (const [index, entry] of spec.entries.entries()) {
      if (!path.resolve(entry.path).startsWith(path.resolve(spec.input_root) + path.sep)) throw new Error('Input outside project');
      const record = {index, file: entry.relative, geometry: entry.identifier, source_sha256: entry.sha256};
      let opened;
      try {
        const raw = JSON.parse(fs.readFileSync(entry.path, 'utf8'));
        const geometry = raw['minecraft:geometry'][entry.index];
        if (geometry.description.identifier !== entry.identifier) throw new Error('Geometry identity changed');
        Codecs.bedrock.load({format_version: raw.format_version, 'minecraft:geometry': [geometry]}, {path: '', no_file: true});
        opened = Project;
        Validator.validate();
        await new Promise(resolve => setTimeout(resolve, 70));
        const compiled = Codecs.bedrock.compile({raw: true});
        record.cubes = Cube.all.length;
        record.bones = Group.all.length;
        record.errors = Validator.errors.map(item => String(item.message || item));
        record.warnings = Validator.warnings.map(item => String(item.message || item));
        record.nonfinite_meshes = Cube.all.filter(cube => {
          const vertices = cube.mesh?.geometry?.attributes?.position?.array;
          return vertices && Array.from(vertices).some(value => !Number.isFinite(value));
        }).map(cube => cube.name);
        const exportName = String(index).padStart(4, '0') + '.geo.json';
        fs.writeFileSync(path.join(expectedOut, exportName), JSON.stringify(compiled, null, 2) + '\n');
        record.export = exportName;
        record.codec_completed = true;
      } catch (error) {
        record.error = String(error.stack || error);
        record.codec_completed = false;
      } finally {
        if (opened) { opened.saved = true; await opened.close(); }
      }
      results.push(record);
      fs.writeFileSync(path.join(expectedOut, 'progress.json'), JSON.stringify({editor: Blockbench.version, completed: results.length, total: spec.entries.length, source_read_only: true, minecraft_client_acceptance: false, results}, null, 2));
      Blockbench.setStatusBarText('Senra model audit: ' + results.length + '/' + spec.entries.length);
    }
    Blockbench.setStatusBarText('Senra model audit complete: ' + results.length);
    Blockbench.showQuickMessage('Senra model audit complete', 5000);
  }
  async function previewHeld() {
    const spec = JSON.parse(fs.readFileSync(input, 'utf8'));
    if (spec.output_root !== path.dirname(input) + '/native-blockbench') throw new Error('Unexpected output root');
    const out = spec.output_root + '/held-previews';
    fs.mkdirSync(out, {recursive: true});
    const records = [];
    for (const item of spec.held_previews) {
      if (!path.resolve(item.texture).startsWith(path.resolve(spec.input_root) + path.sep)) throw new Error('Texture outside project');
      for (const alias of (item.poses || ['fp_right', 'tp_right'])) {
        if(item.java_model) Codecs.java_block.load(item.java_model, {path:'',no_file:true});
        else Codecs.bedrock.load({format_version: '1.21.0', 'minecraft:geometry': [item.geometry]}, {path: '', no_file: true});
        const opened = Project;
        Project.name = item.name + '_' + alias;
        const texture = new Texture({name: item.name + '.png'}).fromPath(item.texture).add();
        if(!item.java_model) Cube.all.forEach(cube => cube.applyTexture(texture, true));
        let animation;
        if(item.java_model) { Modes.options.display.select(); if(alias.startsWith('fp')) DisplayMode.loadFirstRight(); else DisplayMode.loadThirdRight(); } else {
        const data = item.animations[alias];
        [animation] = AnimationCodec.codecs.bedrock.loadFile({json: {format_version: '1.8.0', animations: {[data.id]: data.data}}, path: ''});
        Modes.options.animate.select();
        animation.select();
        Timeline.setTime(0);
        BarItems.bedrock_animation_mode.set(alias.startsWith('fp') ? 'attachable_first' : 'attachable_third');
        BarItems.bedrock_animation_mode.onChange();
        Animator.preview(); }
        await new Promise(resolve => setTimeout(resolve, 400));
        const name = item.name + '_' + alias + '.png';
        await new Promise(resolve => Screencam.screenshotPreview(Preview.selected, {width: 768, height: 768, crop: false}, url => {
          fs.writeFileSync(out + '/' + name, Buffer.from(url.split(',')[1], 'base64'));
          resolve();
        }));
        records.push({camera:{pos:Preview.selected.camera.position.toArray(),rot:Preview.selected.camera.rotation.toArray()},cubes:Cube.all.map(c=>({name:c.name,from:c.from,to:c.to,world:c.mesh.matrixWorld.toArray(),visible:c.mesh.visible})),texture:{width:texture.width,height:texture.height,source_texture_name:texture.name},modelMatrix:Project.model_3d.matrixWorld.toArray(),groups: Group.all.map(g => ({name:g.name,origin:g.origin,position:g.mesh.position.toArray(),rotation:g.mesh.rotation.toArray(),scale:g.mesh.scale.toArray(),binding:g.bedrock_binding})),animation:animation ? animation.getUndoCopy() : null,item: item.name, pose: alias, image: name, native_blockbench_attachable_mode: !item.java_model, merged_contents_for_preview_only: item.merged_contents_for_preview_only, minecraft_client_acceptance: false});
        fs.writeFileSync(out + '/report.json', JSON.stringify(records, null, 2));
        opened.saved = true;
        await opened.close();
      }
    }
    Blockbench.showQuickMessage('Held previews complete', 5000);
  }
  Plugin.register('senra_model_audit', {
    title: 'Senra Read-only Model Audit', author: 'dot', version: '1.0.0',
    description: 'Read only Grilling models; run native Bedrock codec and Validator; write reports to a dedicated audit directory. No network.',
    icon: 'fact_check', variant: 'desktop', min_version: '5.2.1', tags: ['Minecraft: Bedrock Edition'],
    onload() {
      action = new Action('senra_model_audit_run', {name: 'Audit Senra Models (Read-only)', icon: 'fact_check', click() {choose(audit);}});
      MenuBar.addAction(action, 'tools');
      heldAction = new Action('senra_held_preview_run', {name: 'Preview Senra Held Models (Read-only)', icon: 'pan_tool', click() {choose(previewHeld);}});
      MenuBar.addAction(heldAction, 'tools');
    },
    onunload() { if (action) action.delete(); if (heldAction) heldAction.delete(); }
  });
})();
