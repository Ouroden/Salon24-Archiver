
function last(N) {
    return db.Blogs.find().skip(db.Blogs.count()-N);
}

function one() {
    return db.Blogs.findOne();
}
