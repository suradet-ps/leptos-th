# การทดสอบคอมโพเนนต์ของคุณ

การทดสอบส่วนติดต่อผู้ใช้อาจค่อนข้างยุ่งยาก แต่ก็สำคัญมาก บทความนี้จะพูดถึง
หลักการและแนวทางสองสามข้อสำหรับการทดสอบแอป Leptos

## 1. ทดสอบตรรกะทางธุรกิจด้วยการทดสอบ Rust ธรรมดา

ในหลายกรณี การดึงตรรกะออกมาจากคอมโพเนนต์ของคุณแล้วทดสอบแยกต่างหากเป็นเรื่องที่
สมเหตุสมผล สำหรับคอมโพเนนต์ง่ายๆ บางตัว ไม่มีตรรกะอะไรให้ทดสอบเป็นพิเศษ แต่สำหรับ
หลายๆ ตัว การใช้ชนิดตัวห่อที่ทดสอบได้และอิมพลีเมนต์ตรรกะในบล็อก `impl` ของ Rust
ธรรมดานั้นคุ้มค่า

ตัวอย่างเช่น แทนที่จะฝังตรรกะไว้ในคอมโพเนนต์โดยตรงแบบนี้:

```rust
#[component]
pub fn TodoApp() -> impl IntoView {
    let (todos, set_todos) = signal(vec![Todo { /* ... */ }]);
    // ⚠️ this is hard to test because it's embedded in the component
    let num_remaining = move || todos.read().iter().filter(|todo| !todo.completed).sum();
}
```

คุณสามารถดึงตรรกะนั้นออกมาไว้ในโครงสร้างข้อมูลแยกต่างหากและทดสอบมันได้:

```rust
pub struct Todos(Vec<Todo>);

impl Todos {
    pub fn num_remaining(&self) -> usize {
        self.0.iter().filter(|todo| !todo.completed).sum()
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn test_remaining() {
        // ...
    }
}

#[component]
pub fn TodoApp() -> impl IntoView {
    let (todos, set_todos) = signal(Todos(vec![Todo { /* ... */ }]));
    // ✅ this has a test associated with it
    let num_remaining = move || todos.read().num_remaining();
}
```

โดยทั่วไป ยิ่งตรรกะของคุณถูกห่อไว้ในตัวคอมโพเนนต์น้อยลงเท่าไร โค้ดของคุณก็จะยิ่ง
ดูเป็นสำนวน Rust ที่ดีขึ้นและทดสอบได้ง่ายขึ้นเท่านั้น

## 2. ทดสอบคอมโพเนนต์ด้วยการทดสอบแบบเอนด์ทูเอนด์ (`e2e`)

ไดเรกทอรี [`examples`](https://github.com/leptos-rs/leptos/tree/main/examples) ของเรามีตัวอย่างหลายชิ้นที่มาพร้อมการทดสอบแบบเอนด์ทูเอนด์อย่างครอบคลุม โดยใช้เครื่องมือทดสอบที่แตกต่างกัน

วิธีที่ง่ายที่สุดในการดูวิธีใช้เครื่องมือเหล่านี้คือการดูตัวอย่างการทดสอบด้วยตัวเอง:

### `wasm-bindgen-test` กับ [`counter`](https://github.com/leptos-rs/leptos/blob/main/examples/counter/tests/web.rs)

นี่เป็นการตั้งค่าการทดสอบแบบแมนนวลที่ค่อนข้างง่าย ซึ่งใช้คำสั่ง [`wasm-pack test`](https://rustwasm.github.io/wasm-pack/book/commands/test.html)

#### ตัวอย่างการทดสอบ

```rust
#[wasm_bindgen_test]
async fn clear() {
    let document = document();
    let test_wrapper = document.create_element("section").unwrap();
    let _ = document.body().unwrap().append_child(&test_wrapper);

    // start by rendering our counter and mounting it to the DOM
    // note that we start at the initial value of 10
    let _dispose = mount_to(
        test_wrapper.clone().unchecked_into(),
        || view! { <SimpleCounter initial_value=10 step=1/> },
    );

    // now we extract the buttons by iterating over the DOM
    // this would be easier if they had IDs
    let div = test_wrapper.query_selector("div").unwrap().unwrap();
    let clear = test_wrapper
        .query_selector("button")
        .unwrap()
        .unwrap()
        .unchecked_into::<web_sys::HtmlElement>();

    // now let's click the `clear` button
    clear.click();

    // the reactive system is built on top of the async system, so changes are not reflected
    // synchronously in the DOM
    // in order to detect the changes here, we'll just yield for a brief time after each change,
    // allowing the effects that update the view to run
    tick().await;

    // now let's test the <div> against the expected value
    // we can do this by testing its `outerHTML`
    assert_eq!(div.outer_html(), {
        // it's as if we're creating it with a value of 0, right?
        let (value, _set_value) = signal(0);

        // we can remove the event listeners because they're not rendered to HTML
        view! {
            <div>
                <button>"Clear"</button>
                <button>"-1"</button>
                <span>"Value: " {value} "!"</span>
                <button>"+1"</button>
            </div>
        }
        // Leptos supports multiple backend renderers for HTML elements
        // .into_view() here is just a convenient way of specifying "use the regular DOM renderer"
        .into_view()
        // views are lazy -- they describe a DOM tree but don't create it yet
        // calling .build() will actually build the DOM elements
        .build()
        // .build() returned an ElementState, which is a smart pointer for
        // a DOM element. So we can still just call .outer_html(), which access the outerHTML on
        // the actual DOM element
        .outer_html()
    });

    // There's actually an easier way to do this...
    // We can just test against a <SimpleCounter/> with the initial value 0
    assert_eq!(test_wrapper.inner_html(), {
        let comparison_wrapper = document.create_element("section").unwrap();
        let _dispose = mount_to(
            comparison_wrapper.clone().unchecked_into(),
            || view! { <SimpleCounter initial_value=0 step=1/>},
        );
        comparison_wrapper.inner_html()
    });
}
```

### [Playwright กับ `counters`](https://github.com/leptos-rs/leptos/tree/main/examples/counters/e2e)

การทดสอบเหล่านี้ใช้เครื่องมือทดสอบ JavaScript ยอดนิยมอย่าง Playwright เพื่อรันการทดสอบแบบเอนด์ทูเอนด์บนตัวอย่างเดียวกัน โดยใช้ไลบรารีและแนวทางการทดสอบที่คุ้นเคยสำหรับหลายๆ คนที่เคยพัฒนาฟรอนต์เอนด์มาก่อน

#### ตัวอย่างการทดสอบ

```js
test.describe("Increment Count", () => {
  test("should increase the total count", async ({ page }) => {
    const ui = new CountersPage(page);
    await ui.goto();
    await ui.addCounter();

    await ui.incrementCount();
    await ui.incrementCount();
    await ui.incrementCount();

    await expect(ui.total).toHaveText("3");
  });
});
```

### [การทดสอบ Gherkin/Cucumber กับ `todo_app_sqlite`](https://github.com/leptos-rs/leptos/blob/main/examples/todo_app_sqlite/e2e/README.md)

คุณสามารถผสานเครื่องมือทดสอบใดก็ได้ที่คุณต้องการเข้ากับเวิร์กโฟลว์นี้ ตัวอย่างนี้ใช้ Cucumber ซึ่งเป็นเฟรมเวิร์กการทดสอบที่อิงภาษาธรรมชาติ

```
@add_todo
Feature: Add Todo

    Background:
        Given I see the app

    @add_todo-see
    Scenario: Should see the todo
        Given I set the todo as Buy Bread
        When I click the Add button
        Then I see the todo named Buy Bread

    # @allow.skipped
    @add_todo-style
    Scenario: Should see the pending todo
        When I add a todo as Buy Oranges
        Then I see the pending todo
```

นิยามของการกระทำเหล่านี้ถูกกำหนดไว้ในโค้ด Rust

```rust
use crate::fixtures::{action, world::AppWorld};
use anyhow::{Ok, Result};
use cucumber::{given, when};

#[given("I see the app")]
#[when("I open the app")]
async fn i_open_the_app(world: &mut AppWorld) -> Result<()> {
    let client = &world.client;
    action::goto_path(client, "").await?;

    Ok(())
}

#[given(regex = "^I add a todo as (.*)$")]
#[when(regex = "^I add a todo as (.*)$")]
async fn i_add_a_todo_titled(world: &mut AppWorld, text: String) -> Result<()> {
    let client = &world.client;
    action::add_todo(client, text.as_str()).await?;

    Ok(())
}

// etc.
```

### เรียนรู้เพิ่มเติม

เชิญดูการตั้งค่า CI ในรีโพของ Leptos เพื่อเรียนรู้เพิ่มเติมเกี่ยวกับวิธีใช้เครื่องมือเหล่านี้ในแอปพลิเคชันของคุณเอง วิธีการทดสอบทั้งหมดนี้ถูกรันเป็นประจำกับแอปตัวอย่าง Leptos จริงๆ
