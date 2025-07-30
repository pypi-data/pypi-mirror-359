from git import Repo


def clone(repo_url: str, local_dir: str, branch_name: str = "master") -> Repo:
    """
    克隆远端Git工程到本地

    :param repo_url: 工程地址
    :param local_dir: 克隆到本地的文件夹。local_dir内直接就是工程内容了，不单独再包一层工程名
    :param branch_name: 要拉取的分支
    :return: Repo对象，用于Git操作
    """
    return Repo.clone_from(repo_url, local_dir, branch=branch_name)


def repo_from_dir(local_dir: str) -> Repo:
    """
    从本地Git目录获取Repo对象

    :param local_dir: 本地Git目录
    :return: Repo对象，用于Git操作
    """
    return Repo(local_dir)


def create_branch(repo: Repo, branch_name: str, checkout: bool = True) -> None:
    """
    创建分支

    :param repo: Repo对象
    :param branch_name: 要创建的分支名
    """
    if checkout:
        repo.git.checkout('-b', branch_name)
    else:
        repo.create_head(branch_name)


def add_all(repo: Repo, add: bool = True):
    """
    add所有文件

    :param repo: Repo对象
    :param add: True：add；False：取消add
    :return:
    """
    if add:
        repo.index.add([''])
    else:
        repo.index.reset()


def add(repo: Repo, paths: list[str], add: bool = True):
    """
    add所有文件

    :param repo: Repo对象
    :param paths: 待操作的所有文件的路径
    :param add: True：add；False：取消add
    :return:
    """
    if paths is None or len(paths) == 0:
        return

    if add:
        repo.index.add(paths)
    else:
        repo.git.reset(paths)


def commit(repo: Repo, message: str):
    """
    commit

    :param repo: Repo对象
    :param message: commit信息
    """
    repo.index.commit(message)


def push(repo: Repo, branch_name: str, remote_name: str = 'origin'):
    """
    push

    :param repo: Repo对象
    :param branch_name: 要push的分支名
    :param remote_name: 远端域，一般是origin
    """
    repo.remote(name=remote_name).push(refspec=f"{branch_name}:{branch_name}")
