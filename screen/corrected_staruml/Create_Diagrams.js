// Выполните файл целиком в StarUML через View → Script Console.
// Код добавляет три диаграммы в открытый проект.

(function createDiagrams(app, type) {
  const project = app.project.getProject();
  if (!project) throw new Error('Создайте или откройте проект в StarUML.');

  function add(parent, item, property = 'ownedElements') {
    item._parent = parent;
    parent[property].push(item);
    return item;
  }

  function model(typeName, name, parent, property) {
    const item = new type[typeName]();
    item.name = name;
    return add(parent, item, property);
  }

  function format(item, fontSize) {
    item.font.face = 'Arial';
    item.font.size = fontSize;
    item.fontColor = '#171717';
    item.lineColor = '#404040';
    item.fillColor = '#ffffff';
    item.showShadow = false;
    for (const child of item.subViews) format(child, fontSize);
    return item;
  }

  function shape(diagram, typeName, item, [left, top, width, height], fontSize = 16, shadow = false) {
    const view = format(new type[typeName](), fontSize);
    Object.assign(view, { model: item, left, top, width, height, showShadow: shadow });
    return add(diagram, view, 'ownedViews');
  }

  function edge(diagram, typeName, item, tail, head, coordinates, lineStyle = type.EdgeView.LS_OBLIQUE, fontSize = 16) {
    const view = format(new type[typeName](), fontSize);
    Object.assign(view, { model: item, tail, head, lineStyle });
    view.points.clear();
    for (const [x, y] of coordinates) view.points.add(new type.Point(x, y));
    return add(diagram, view, 'ownedViews');
  }

  function contain(parent, child) {
    child.containerView = parent;
    parent.containedViews.push(child);
    return child;
  }

  const root = new type.UMLModel();
  root.name = 'Прогноз нагрузки на сервер';

  const data = model('ERDDataModel', 'Данные паттернов нагрузки', root);
  const er = model('ERDDiagram', '01 ER диаграмма', data);
  er.defaultDiagram = true;
  er.documentation = 'Основные поля по образцу ER. N обозначает возможность NULL. По кнопке «Далее» обязательно название, описание и медиа необязательны. RPS, пиковый коэффициент и длительность задаются при публикации. Даты и поля, используемые для расчёта ресурсов, приведены в таблице физической БД РПЗ.';
  const patternEntity = model('ERDEntity', 'load_patterns', data);
  const likeEntity = model('ERDEntity', 'pattern_likes', data);
  const userEntity = model('ERDEntity', 'users', data);

  function column(entity, name, sqlType, { length = '', primaryKey = false, nullable = false, unique = false, referenceTo = null } = {}) {
    const item = model('ERDColumn', name, entity, 'columns');
    Object.assign(item, { type: sqlType, length, primaryKey, nullable, unique });
    if (referenceTo) Object.assign(item, { foreignKey: true, referenceTo });
    return item;
  }

  const userId = column(userEntity, 'id', 'INTEGER', { primaryKey: true });
  column(userEntity, 'username', 'VARCHAR', { length: '50', unique: true });
  column(userEntity, 'password_hash', 'VARCHAR', { length: '255', nullable: true });
  column(userEntity, 'email', 'VARCHAR', { length: '100', unique: true });
  const patternId = column(patternEntity, 'id', 'INTEGER', { primaryKey: true });
  column(patternEntity, 'pattern_name', 'VARCHAR', { length: '100' });
  column(patternEntity, 'description', 'TEXT', { nullable: true });
  column(patternEntity, 'requests_per_second', 'INTEGER', { nullable: true });
  column(patternEntity, 'peak_multiplier', 'DOUBLE PRECISION', { nullable: true });
  column(patternEntity, 'duration_hours', 'INTEGER', { nullable: true });
  column(patternEntity, 'image_url', 'VARCHAR', { length: '500', nullable: true });
  column(patternEntity, 'video_url', 'VARCHAR', { length: '500', nullable: true });
  column(patternEntity, 'status', 'patternstatus');
  column(patternEntity, 'creator_id', 'INTEGER', { referenceTo: userId });
  column(patternEntity, 'created_at', 'TIMESTAMP', { nullable: true });
  column(likeEntity, 'id', 'INTEGER', { primaryKey: true });
  column(likeEntity, 'user_id', 'INTEGER', { referenceTo: userId });
  column(likeEntity, 'pattern_id', 'INTEGER', { referenceTo: patternId });
  likeEntity.documentation = 'Одна отметка на пару user_id и pattern_id.';

  const erPattern = shape(er, 'ERDEntityView', patternEntity, [24, 24, 350, 242], 16, true);
  const erLike = shape(er, 'ERDEntityView', likeEntity, [486, 24, 256, 85], 16, true);
  const erUser = shape(er, 'ERDEntityView', userEntity, [486, 197, 256, 104], 16, true);

  function erLink(one, many, positions) {
    const relationship = model('ERDRelationship', '', one.model);
    Object.assign(relationship.end1, { reference: one.model, cardinality: '1' });
    Object.assign(relationship.end2, { reference: many.model, cardinality: '0..*' });
    return edge(er, 'ERDRelationshipView', relationship, one, many, positions, type.EdgeView.LS_RECTILINEAR);
  }

  erLink(erPattern, erLike, [[374, 66], [486, 66]]);
  erLink(erUser, erLike, [[614, 197], [614, 109]]);
  erLink(erUser, erPattern, [[486, 228], [374, 228]]);

  const frontend = model('UMLPackage', 'Фронтенд', root);
  const web = model('UMLPackage', 'Веб-сервис', root);
  const orm = model('UMLPackage', 'Модель', root);
  const database = model('UMLPackage', 'База данных', root);
  const classes = model('UMLClassDiagram', '02 Диаграмма классов', root);
  const layers = [
    [frontend, [24, 24, 920, 182]],
    [web, [24, 333, 920, 288]],
    [orm, [24, 671, 920, 150]],
    [database, [24, 869, 920, 153]]
  ].map(([item, bounds]) => shape(classes, 'UMLPackageView', item, bounds, 19, true));

  function classBox(item, layer, bounds, { fontSize = 17, wrap = false, table = false } = {}) {
    const view = shape(classes, 'UMLClassView', item, bounds, fontSize, true);
    Object.assign(view, {
      suppressAttributes: table,
      suppressOperations: table,
      suppressReceptions: true,
      stereotypeDisplay: 'none',
      showType: false,
      showVisibility: true,
      showOperationSignature: true,
      wordWrap: wrap
    });
    return contain(layer, view);
  }

  const pages = [
    ['Плитка всех паттернов нагрузки', 36, 202],
    ['Лента паттернов нагрузки', 248, 191],
    ['Добавление паттерна нагрузки', 449, 226],
    ['Регистрация пользователя', 689, 244]
  ].map(([name, x, width]) => classBox(model('UMLClass', name, frontend), layers[0],
    [x, 76, width, 91], { wrap: true }));
  const patterns = model('UMLClass', 'Домен паттернов /api/load_patterns', web);
  const users = model('UMLClass', 'Домен пользователей /api/users', web);
  const operations = {};
  for (const [domain, methods] of [
    [patterns, [
      ['list', 'GET /api/load_patterns'],
      ['feed', 'GET /api/load_patterns/feed'],
      ['draft', 'GET /api/load_patterns/draft'],
      ['detail', 'GET /api/load_patterns/{id}'],
      ['create', 'POST /api/load_patterns'],
      ['publish', 'PUT /api/load_patterns/{id}/publish'],
      ['delete', 'DELETE /api/load_patterns/{id}'],
      ['like', 'POST /api/load_patterns/{id}/like']
    ]],
    [users, [
      ['register', 'POST /api/users/register'],
      ['login', 'POST /api/users/login'],
      ['logout', 'POST /api/users/logout']
    ]]
  ]) {
    for (const [key, name] of methods) {
      operations[key] = model('UMLOperation', name, domain, 'operations');
      operations[key].visibility = 'public';
    }
  }
  const patternDomain = classBox(patterns, layers[1], [43, 390, 449, 208], { fontSize: 17 });
  const userDomain = classBox(users, layers[1], [546, 390, 357, 122], { fontSize: 17 });

  function interfaceBox(name, bounds) {
    const item = model('UMLInterface', name, web);
    const view = shape(classes, 'UMLInterfaceView', item, bounds, 16);
    Object.assign(view, { stereotypeDisplay: 'icon', suppressAttributes: true, suppressOperations: true });
    return view;
  }

  const patternApi = interfaceBox('API load_patterns', [125, 237, 173, 45]);
  const userApi = interfaceBox('API users', [655, 237, 140, 45]);

  function link(source, target, points, realization = false) {
    const typeName = realization ? 'UMLInterfaceRealization' : 'UMLDependency';
    const item = model(typeName, '', source.model);
    Object.assign(item, { source: source.model, target: target.model });
    return edge(classes, typeName + 'View', item, source, target, points);
  }

  pages.slice(0, 3).forEach(page => link(page, patternApi, [[page.left + page.width / 2, 167], [211, 249]]));
  link(pages[3], userApi, [[811, 167], [725, 249]]);
  link(patternDomain, patternApi, [[296, 390], [297, 249], [211, 249]], true);
  link(userDomain, userApi, [[795, 390], [795, 249], [725, 249]], true);

  const positions = [[64, 181], [386, 181], [717, 181]];
  const models = ['LoadPattern', 'PatternLike', 'User'].map((name, i) => {
    const [x, w] = positions[i];
    return classBox(model('UMLClass', name, orm), layers[2], [x, 733, w, 64]);
  });
  const tables = ['load_patterns', 'pattern_likes', 'users'].map((name, i) => {
    const [x, w] = positions[i];
    return classBox(model('UMLClass', name, database), layers[3], [x, 936, w, 45], { table: true });
  });
  link(patternDomain, models[0], [[156, 598], [156, 733]]);
  link(patternDomain, models[1], [[295, 598], [476, 733]]);
  link(patternDomain, models[2], [[468, 598], [806, 733]]);
  link(userDomain, models[2], [[726, 512], [807, 733]]);
  for (const [i, ormView] of models.entries()) {
    const x = ormView.left + ormView.width / 2;
    const anchor = i === 1 ? ormView.left + 15 : x;
    link(ormView, tables[i], [[x, 797], [anchor, 842], [anchor, 907], [x, 936]]);
  }

  function association(tail, head, tailMultiplicity, headMultiplicity, coordinates, lineStyle) {
    const item = model('UMLAssociation', '', tail.model);
    Object.assign(item.end1, { reference: tail.model, multiplicity: tailMultiplicity });
    Object.assign(item.end2, { reference: head.model, multiplicity: headMultiplicity });
    const view = edge(classes, 'UMLAssociationView', item, tail, head, coordinates, lineStyle, 15);
    view.tailMultiplicityLabel.distance = 18;
    view.headMultiplicityLabel.distance = 18;
    return view;
  }

  association(tables[0], tables[1], '1', '0..*', [[245, 958], [386, 958]]);
  association(tables[1], tables[2], '0..*', '1', [[567, 958], [717, 958]]);
  association(tables[0], tables[2], '0..*', '1', [[154, 981], [154, 1004], [807, 1004], [807, 981]], type.EdgeView.LS_ROUNDRECT);

  const collaboration = model('UMLCollaboration', 'Публикация и просмотр паттерна', root);
  const interaction = model('UMLInteraction', 'Диаграмма последовательности', collaboration);
  const sequence = model('UMLSequenceDiagram', '03 Диаграмма последовательности', interaction);
  Object.assign(sequence, { showSequenceNumber: true, showSignature: true, showActivation: true });
  shape(sequence, 'UMLFrameView', interaction, [24, 8, 920, 1071], 17);

  const participants = [
    ['Фронтенд', '', 37, 140],
    [': Домен users', users, 403, 162],
    [': Домен load_patterns', patterns, 740, 191]
  ].map(([name, domain, x, width]) => {
    const line = model('UMLLifeline', name, interaction, 'participants');
    const role = model('UMLAttribute', '', collaboration, 'attributes');
    role.type = domain;
    line.represent = role;
    const view = shape(sequence, 'UMLSeqLifelineView', line, [x, 40, width, 998], 16, true);
    view.showType = false;
    return view;
  });

  const cookie = 'Cookie: session_id';
  const exchanges = [
    [1, 'login', 'username, password', '200 JSON(message), Set-Cookie: session_id'],
    [2, 'list', 'max_expected, ' + cookie, '200 JSON(items[], total)'],
    [2, 'create', 'pattern_name, video, image, ' + cookie, '201 JSON(PatternResponse)'],
    [2, 'draft', cookie, '200 JSON(PatternResponse)'],
    [2, 'publish', 'requests_per_second, peak_multiplier, duration_hours, ' + cookie, '200 JSON(PatternResponse)'],
    [2, 'feed', cookie, '200 JSON(id, …, likes_count, is_liked)'],
    [2, 'detail', 'next=true, ' + cookie, '200 JSON(id, …, likes_count, is_liked)'],
    [2, 'like', 'value=1, ' + cookie, '200 JSON(message)']
  ];

  function message(source, target, name, y, signature, args) {
    const item = model('UMLMessage', name, interaction, 'messages');
    Object.assign(item, {
      source: source.model,
      target: target.model,
      signature,
      arguments: args,
      messageSort: signature ? 'synchCall' : 'reply'
    });
    const view = edge(sequence, 'UMLSeqMessageView', item, source.linePart, target.linePart,
      [[source.left + source.width / 2, y], [target.left + target.width / 2, y]],
      type.EdgeView.LS_RECTILINEAR, args.length > 65 ? 14 : 16);
    view.showType = false;
    view.nameLabel.distance = 13;
    if (signature) view.activation.height = 37;
    return view;
  }

  for (const [i, [target, name, args, reply]] of exchanges.entries()) {
    const y = 210 + i * 105;
    message(participants[0], participants[target], '', y, operations[name], args);
    message(participants[target], participants[0], reply, y + 34, null, '');
  }

  const payload = JSON.parse(app.repository.writeObject(root));
  delete payload._parent;
  const imported = app.project.importFromJson(project, payload);
  app.preferences.set('diagramEditor.showGrid', false);
  app.diagrams.setCurrentDiagram(imported.ownedElements.find(item => item instanceof type.ERDDataModel).ownedElements[0]);
  console.log('Добавлены ER, диаграмма классов и диаграмма последовательности.');
  return imported;
})(app, type);
